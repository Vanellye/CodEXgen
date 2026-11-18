package main

import (
	"bufio"
	"crypto/rand"
	"crypto/sha256"
	"crypto/subtle"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"os"
	"path/filepath"
	"regexp"
	"strings"
	"sync"
	"time"
)

const genesisHash = "0000000000000000000000000000000000000000000000000000000000000000"
const maxBodyBytes = 16 << 10

var categories = map[string]bool{"Reference": true, "Architecture": true, "Research": true, "Governance": true, "Implementation": true, "Other": true}
var intentScopes = map[string]bool{"publish_wiki": true, "background_dispatch": true}
var uuidPattern = regexp.MustCompile(`(?i)^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$`)

type Link struct {
	ID          string    `json:"id"`
	URL         string    `json:"url"`
	Title       string    `json:"title"`
	Category    string    `json:"category"`
	Description string    `json:"description"`
	Source      string    `json:"source"`
	CreatedAt   time.Time `json:"createdAt"`
}

type Intent struct {
	ID              string    `json:"id"`
	Scope           string    `json:"scope"`
	Reason          string    `json:"reason"`
	RecordedAt      time.Time `json:"recordedAt"`
	ExecutionEnabled bool     `json:"executionEnabled"`
}

type Event struct {
	Seq          int             `json:"seq"`
	At           time.Time       `json:"at"`
	Type         string          `json:"type"`
	Payload      json.RawMessage `json:"payload"`
	PreviousHash string          `json:"previousHash"`
	Hash         string          `json:"hash,omitempty"`
}

type Service struct {
	mu       sync.Mutex
	token    string
	ledger   string
	events   []Event
	sequence int
	previous string
}

func eventHash(e Event) (string, error) {
	e.Hash = ""
	b, err := json.Marshal(e)
	if err != nil { return "", err }
	sum := sha256.Sum256(b)
	return hex.EncodeToString(sum[:]), nil
}

func openService(dataDir, token string) (*Service, error) {
	if len(token) < 32 { return nil, errors.New("ERIA_API_TOKEN must contain at least 32 characters") }
	if strings.TrimSpace(dataDir) == "" { return nil, errors.New("ERIA_DATA_DIR is required") }
	if err := os.MkdirAll(dataDir, 0700); err != nil { return nil, err }
	s := &Service{token: token, ledger: filepath.Join(dataDir, "events.jsonl"), previous: genesisHash}
	f, err := os.Open(s.ledger)
	if err != nil && !os.IsNotExist(err) { return nil, err }
	if err == nil {
		defer f.Close()
		scanner := bufio.NewScanner(f)
		scanner.Buffer(make([]byte, 4096), 1<<20)
		for scanner.Scan() {
			var e Event
			if err := json.Unmarshal(scanner.Bytes(), &e); err != nil { return nil, errors.New("ERIA ledger integrity failure: invalid JSON") }
			expected, err := eventHash(e)
			if err != nil { return nil, err }
			if e.Seq != s.sequence+1 || e.PreviousHash != s.previous || e.Hash == "" || !equalHash(e.Hash, expected) {
				return nil, fmt.Errorf("ERIA ledger integrity failure at sequence %d; refusing to start", s.sequence+1)
			}
			s.events = append(s.events, e)
			s.sequence, s.previous = e.Seq, e.Hash
		}
		if err := scanner.Err(); err != nil { return nil, err }
	}
	return s, nil
}

func equalHash(a, b string) bool {
	if len(a) != len(b) { return false }
	return subtle.ConstantTimeCompare([]byte(a), []byte(b)) == 1
}

func (s *Service) append(kind string, payload any) (Event, error) {
	s.mu.Lock()
	defer s.mu.Unlock()
	raw, err := json.Marshal(payload)
	if err != nil { return Event{}, err }
	e := Event{Seq:s.sequence+1, At:time.Now().UTC(), Type:kind, Payload:raw, PreviousHash:s.previous}
	e.Hash, err = eventHash(e)
	if err != nil { return Event{}, err }
	line, err := json.Marshal(e)
	if err != nil { return Event{}, err }
	f, err := os.OpenFile(s.ledger, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0600)
	if err != nil { return Event{}, err }
	if _, err = f.Write(append(line, '\n')); err == nil { err = f.Sync() }
	closeErr := f.Close()
	if err != nil { return Event{}, err }
	if closeErr != nil { return Event{}, closeErr }
	s.events = append(s.events, e)
	s.sequence, s.previous = e.Seq, e.Hash
	return e, nil
}

func (s *Service) snapshot() []Event {
	s.mu.Lock()
	defer s.mu.Unlock()
	out := make([]Event, len(s.events))
	copy(out, s.events)
	return out
}

func (s *Service) links() []Link {
	state := map[string]Link{}
	for _, e := range s.snapshot() {
		switch e.Type {
		case "link.created":
			var link Link
			if json.Unmarshal(e.Payload, &link) == nil { state[link.ID] = link }
		case "link.archived":
			var p struct { ID string `json:"id"` }
			if json.Unmarshal(e.Payload, &p) == nil { delete(state, p.ID) }
		}
	}
	out := make([]Link, 0, len(state))
	for _, link := range state { out = append(out, link) }
	return out
}

func writeJSON(w http.ResponseWriter, status int, body any) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.Header().Set("Cache-Control", "no-store")
	w.Header().Set("X-Content-Type-Options", "nosniff")
	w.Header().Set("Referrer-Policy", "no-referrer")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(body)
}

func decodeBody(w http.ResponseWriter, r *http.Request, dst any) bool {
	r.Body = http.MaxBytesReader(w, r.Body, maxBodyBytes)
	dec := json.NewDecoder(r.Body)
	if err := dec.Decode(dst); err != nil {
		status, msg := http.StatusBadRequest, "Request body must be valid JSON."
		var maxErr *http.MaxBytesError
		if errors.As(err, &maxErr) { status, msg = http.StatusRequestEntityTooLarge, "Request body is too large." }
		writeJSON(w, status, map[string]string{"error":msg})
		return false
	}
	var extra any
	if err := dec.Decode(&extra); err != io.EOF {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error":"Request body must contain one JSON value."})
		return false
	}
	return true
}

func validText(v string, max int, required bool) bool {
	return len(v) <= max && (!required || strings.TrimSpace(v) != "")
}

func (s *Service) authorized(r *http.Request) bool {
	const prefix = "Bearer "
	h := r.Header.Get("Authorization")
	if !strings.HasPrefix(h, prefix) { return false }
	got := []byte(strings.TrimPrefix(h, prefix))
	want := []byte(s.token)
	return len(got) == len(want) && subtle.ConstantTimeCompare(got, want) == 1
}

func (s *Service) handler() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet { writeJSON(w, 405, map[string]string{"error":"Method not allowed."}); return }
		writeJSON(w, 200, map[string]any{"ok":true,"service":"eria-wiki-drop-link","version":1})
	})
	mux.HandleFunc("/api/", func(w http.ResponseWriter, r *http.Request) {
		if !s.authorized(r) { writeJSON(w, 401, map[string]string{"error":"Bearer token required."}); return }
		switch {
		case r.URL.Path == "/api/links" && r.Method == http.MethodGet:
			q := strings.ToLower(strings.TrimSpace(r.URL.Query().Get("q")))
			links := make([]Link, 0)
			for _, l := range s.links() {
				haystack := strings.ToLower(strings.Join([]string{l.Title,l.URL,l.Category,l.Description,l.Source}, " "))
				if strings.Contains(haystack, q) { links = append(links, l) }
			}
			writeJSON(w, 200, map[string]any{"links":links})
		case r.URL.Path == "/api/links" && r.Method == http.MethodPost:
			var body struct { Title string `json:"title"`; URL string `json:"url"`; Category string `json:"category"`; Description string `json:"description"`; Source string `json:"source"` }
			if !decodeBody(w,r,&body) { return }
			if !validText(body.Title,200,true) { writeJSON(w,400,map[string]string{"error":"title must be 1–200 characters."}); return }
			if !validText(body.URL,2048,true) { writeJSON(w,400,map[string]string{"error":"url must be 1–2048 characters."}); return }
			u, err := url.ParseRequestURI(body.URL)
			if err != nil || u.Host == "" || (u.Scheme != "http" && u.Scheme != "https") { writeJSON(w,400,map[string]string{"error":"Only valid HTTP and HTTPS URLs are accepted."}); return }
			if body.Category == "" { body.Category = "Other" }
			if !categories[body.Category] { writeJSON(w,400,map[string]string{"error":"Unsupported category."}); return }
			if !validText(body.Description,2000,false) || !validText(body.Source,500,false) { writeJSON(w,400,map[string]string{"error":"description or source exceeds its allowed length."}); return }
			link := Link{ID:newID(),URL:u.String(),Title:strings.TrimSpace(body.Title),Category:body.Category,Description:strings.TrimSpace(body.Description),Source:strings.TrimSpace(body.Source),CreatedAt:time.Now().UTC()}
			if _, err := s.append("link.created",link); err != nil { writeJSON(w,500,map[string]string{"error":"Unable to persist event."}); return }
			writeJSON(w,201,map[string]any{"link":link})
		case strings.HasPrefix(r.URL.Path,"/api/links/") && r.Method == http.MethodDelete:
			id := strings.TrimPrefix(r.URL.Path,"/api/links/")
			if !uuidPattern.MatchString(id) { writeJSON(w,404,map[string]string{"error":"Link not found."}); return }
			found := false
			for _, l := range s.links() { if l.ID == id { found = true; break } }
			if !found { writeJSON(w,404,map[string]string{"error":"Link not found."}); return }
			if _, err := s.append("link.archived",map[string]string{"id":id}); err != nil { writeJSON(w,500,map[string]string{"error":"Unable to persist event."}); return }
			writeJSON(w,200,map[string]any{"archived":true,"id":id,"recordRetainedInLedger":true})
		case r.URL.Path == "/api/authorization-intents" && r.Method == http.MethodPost:
			var body struct { Scope string `json:"scope"`; Confirmation string `json:"confirmation"`; Reason string `json:"reason"` }
			if !decodeBody(w,r,&body) { return }
			if !intentScopes[body.Scope] { writeJSON(w,400,map[string]string{"error":"Unsupported authorization scope."}); return }
			if body.Confirmation != body.Scope { writeJSON(w,403,map[string]string{"error":"Exact-scope confirmation required."}); return }
			if !validText(body.Reason,1000,false) { writeJSON(w,400,map[string]string{"error":"reason must be 0–1000 characters."}); return }
			intent := Intent{ID:newID(),Scope:body.Scope,Reason:strings.TrimSpace(body.Reason),RecordedAt:time.Now().UTC(),ExecutionEnabled:false}
			if _, err := s.append("authorization.intent",intent); err != nil { writeJSON(w,500,map[string]string{"error":"Unable to persist event."}); return }
			writeJSON(w,201,map[string]any{"intent":intent,"executionEnabled":false})
		case r.URL.Path == "/api/audit" && r.Method == http.MethodGet:
			writeJSON(w,200,map[string]any{"integrity":"verified","entries":s.snapshot()})
		default:
			writeJSON(w,404,map[string]string{"error":"Not found."})
		}
	})
	return mux
}

func newID() string {
	b := make([]byte, 16)
	if _, err := rand.Read(b); err != nil { panic("secure random UUID generation failed: " + err.Error()) }
	b[6] = (b[6] & 0x0f) | 0x40
	b[8] = (b[8] & 0x3f) | 0x80
	return fmt.Sprintf("%08x-%04x-%04x-%04x-%012x", b[0:4], b[4:6], b[6:8], b[8:10], b[10:16])
}

func main() {
	dataDir := os.Getenv("ERIA_DATA_DIR")
	if dataDir == "" { dataDir = "./data" }
	token := os.Getenv("ERIA_API_TOKEN")
	s, err := openService(dataDir, token)
	if err != nil { log.Fatal(err) }
	addr := ":" + os.Getenv("PORT")
	if os.Getenv("PORT") == "" { addr = ":8787" }
	log.Printf("ERIA Wiki Drop-Link API listening on %s", addr)
	log.Fatal(http.ListenAndServe(addr, s.handler()))
}
