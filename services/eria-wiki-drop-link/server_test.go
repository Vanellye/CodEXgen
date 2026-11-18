package main

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

const testToken = "eria-test-token-that-is-at-least-32-characters"

func testService(t *testing.T) (*Service, *httptest.Server) {
	t.Helper()
	s, err := openService(t.TempDir(), testToken)
	if err != nil { t.Fatal(err) }
	ts := httptest.NewServer(s.handler())
	t.Cleanup(ts.Close)
	return s, ts
}

func request(t *testing.T, ts *httptest.Server, method, path, body string, auth bool) *http.Response {
	t.Helper()
	req, err := http.NewRequest(method, ts.URL+path, strings.NewReader(body))
	if err != nil { t.Fatal(err) }
	req.Header.Set("Content-Type","application/json")
	if auth { req.Header.Set("Authorization","Bearer "+testToken) }
	res, err := http.DefaultClient.Do(req)
	if err != nil { t.Fatal(err) }
	return res
}

func TestHealthAndAuthentication(t *testing.T) {
	_, ts := testService(t)
	if res := request(t,ts,"GET","/health","",false); res.StatusCode != 200 { t.Fatalf("health: %d",res.StatusCode) }
	if res := request(t,ts,"GET","/api/links","",false); res.StatusCode != 401 { t.Fatalf("unauthenticated: %d",res.StatusCode) }
}

func TestCreateListArchiveAndAudit(t *testing.T) {
	s, ts := testService(t)
	res := request(t,ts,"POST","/api/links",\`{"title":"ERIA reference","url":"https://example.com/eria","category":"Architecture"}\`,true)
	if res.StatusCode != 201 { t.Fatalf("create: %d",res.StatusCode) }
	var created struct { Link Link \`json:"link"\` }
	if err := json.NewDecoder(res.Body).Decode(&created); err != nil { t.Fatal(err) }
	res.Body.Close()
	if got := len(s.links()); got != 1 { t.Fatalf("links=%d",got) }
	res = request(t,ts,"DELETE","/api/links/"+created.Link.ID,"",true)
	if res.StatusCode != 200 { t.Fatalf("archive: %d",res.StatusCode) }
	res.Body.Close()
	if got := len(s.links()); got != 0 { t.Fatalf("active links after archive=%d",got) }
	if got := len(s.snapshot()); got != 2 { t.Fatalf("audit events=%d",got) }
}

func TestRejectsUnsafeURLAndIntentNeverExecutes(t *testing.T) {
	_, ts := testService(t)
	res := request(t,ts,"POST","/api/links",\`{"title":"unsafe","url":"javascript:alert(1)"}\`,true)
	if res.StatusCode != 400 { t.Fatalf("unsafe URL status=%d",res.StatusCode) }
	res.Body.Close()
	res = request(t,ts,"POST","/api/authorization-intents",\`{"scope":"publish_wiki","confirmation":"publish_wiki","reason":"reviewed"}\`,true)
	if res.StatusCode != 201 { t.Fatalf("intent status=%d",res.StatusCode) }
	var result map[string]any
	if err := json.NewDecoder(res.Body).Decode(&result); err != nil { t.Fatal(err) }
	res.Body.Close()
	if result["executionEnabled"] != false { t.Fatalf("execution unexpectedly enabled: %#v",result) }
}

func TestLedgerTamperingFailsClosed(t *testing.T) {
	dir := t.TempDir()
	s, err := openService(dir,testToken)
	if err != nil { t.Fatal(err) }
	if _, err := s.append("link.created",Link{ID:"x",Title:"original"}); err != nil { t.Fatal(err) }
	file := filepath.Join(dir,"events.jsonl")
	data, err := os.ReadFile(file)
	if err != nil { t.Fatal(err) }
	data = []byte(strings.Replace(string(data),"original","tampered",1))
	if err := os.WriteFile(file,data,0600); err != nil { t.Fatal(err) }
	if _, err := openService(dir,testToken); err == nil || !strings.Contains(err.Error(),"integrity failure") { t.Fatalf("expected integrity failure, got %v",err) }
}
