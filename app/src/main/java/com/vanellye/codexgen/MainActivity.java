package com.vanellye.codexgen;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.os.AsyncTask;
import android.view.View;
import android.view.Gravity;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.inputmethod.InputType;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import android.widget.Toast;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import com.vanellye.codexgen.gitbridge.GitFreedomBridge;
import com.vanellye.codexgen.dataresonance.DataResonanceStore;
import com.vanellye.codexgen.nativebridge.OlpirtNativeBridge;
import com.vanellye.codexgen.consent.ConsentReviewStore;

/** Native Android Views application. No Compose, Kotlin, AndroidX or Lifecycle dependency. */
public final class MainActivity extends Activity {
    private LinearLayout root;
    private FrameLayout content;
    private GitFreedomBridge git;
    private DataResonanceStore data;
    private ConsentReviewStore consentReviews;
    private EditText repositoryUrl, baseBranch, featureBranch, authorName, authorEmail;
    private EditText tokenField, vaultPass, commitMessage, prTitle, prBody, localFilePath, localFileContents;
    private EditText channelField, valueField, unitField, biomarkerField, frequencyField, notesField, correlationA, correlationB;
    private TextView gitStatus;
    private LinearLayout changedFiles;
    private final Map<String, CheckBox> fileChecks = new HashMap<String, CheckBox>();
    private GitFreedomBridge.Config config;
    private static final int REQUEST_WORKSPACE_TREE = 1901;

    private interface Work { String run() throws Exception; }

    public void onCreate(Bundle state) {
        super.onCreate(state);
        git = GitFreedomBridge.shared(this);
        data = new DataResonanceStore(this);
        consentReviews = new ConsentReviewStore(this);
        config = new GitFreedomBridge.Config();
        buildShell();
        showCodeGen();
    }

    private int dp(int n) {
        return (int)(n * getResources().getDisplayMetrics().density + 0.5f);
    }
    private void buildShell() {
        root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding(dp(8), dp(8), dp(8), dp(8));
        LinearLayout nav = new LinearLayout(this);
        nav.setOrientation(LinearLayout.HORIZONTAL);
        String[] labels = new String[]{"CodeGen","Git","Consent","Resonance","Olpirt"};
        for (int i=0;i<labels.length;i++) {
            final int index=i;
            Button b = new Button(this);
            b.setText(labels[i]);
            b.setTextSize(11);
            nav.addView(b,new LinearLayout.LayoutParams(0,dp(48),1));
            b.setOnClickListener(new View.OnClickListener() {
                public void onClick(View v) {
                    if(index==0) showCodeGen();
                    else if(index==1) showGit();
                    else if(index==2) showConsent();
                    else if(index==3) showResonance();
                    else showOlpirt();
                }
            });
        }
        root.addView(nav);
        content = new FrameLayout(this);
        root.addView(content,new LinearLayout.LayoutParams(-1,0,1));
        setContentView(root);
    }
    private LinearLayout page(String title) {
        ScrollView scroll = new ScrollView(this);
        LinearLayout body = new LinearLayout(this);
        body.setOrientation(LinearLayout.VERTICAL);
        body.setPadding(dp(10),dp(10),dp(10),dp(18));
        scroll.addView(body);
        TextView heading = new TextView(this);
        heading.setText(title);
        heading.setTextSize(21);
        heading.setPadding(0,0,0,dp(8));
        body.addView(heading);
        content.removeAllViews();
        content.addView(scroll);
        return body;
    }
    private EditText field(LinearLayout body,String hint,String value,int inputType) {
        EditText e = new EditText(this);
        e.setSingleLine(true);
        e.setHint(hint);
        e.setText(value == null ? "" : value);
        e.setInputType(inputType);
        body.addView(e,new LinearLayout.LayoutParams(-1,dp(48)));
        return e;
    }
    private Button button(LinearLayout body,String label,View.OnClickListener listener) {
        Button b = new Button(this);
        b.setText(label);
        body.addView(b,new LinearLayout.LayoutParams(-1,dp(48)));
        b.setOnClickListener(listener);
        return b;
    }
    private TextView label(LinearLayout body,String text) {
        TextView t = new TextView(this);
        t.setText(text);
        t.setPadding(0,dp(6),0,dp(4));
        body.addView(t);
        return t;
    }
    private void status(TextView target,String text) {
        target.setText(text == null ? "" : text);
    }
    private void runWork(final TextView target,final Work work) {
        target.setText("Working...");
        new AsyncTask<Void,Void,String>() {
            protected String doInBackground(Void... unused) {
                try { return work.run(); }
                catch (Exception e) { return "Operation failed: " + e.getMessage(); }
            }
            protected void onPostExecute(String result) {
                target.setText(result);
            }
        }.execute();
    }

    private void showCodeGen() {
        LinearLayout body=page("CodEXgen Studio");
        label(body,"Generate a simple Python module scaffold locally.");
        final EditText name=field(body,"Module name","StrideModule",InputType.TYPE_CLASS_TEXT);
        final TextView output=new TextView(this);
        output.setTextIsSelectable(true);
        output.setText("Enter a module name and generate a scaffold.");
        button(body,"Generate code",new View.OnClickListener(){
            public void onClick(View v){
                String n=name.getText().toString().trim();
                if(n.length()==0){output.setText("Module name is required.");return;}
                if(!Character.isLetter(n.charAt(0)) && n.charAt(0)!='_'){output.setText("Use a valid Python identifier.");return;}
                for(int i=0;i<n.length();i++){
                    char c=n.charAt(i);
                    if(!Character.isLetterOrDigit(c) && c!='_'){output.setText("Use a valid Python identifier.");return;}
                }
                output.setText("# Generated by CodEXgen\nclass "+n+":\n    def __init__(self, data=None):\n        self.data = data or {}\n\n    def snapshot(self):\n        return dict(self.data)\n");
            }
        });
        body.addView(output,new LinearLayout.LayoutParams(-1,-2));
    }

    private void readConfig() {
        config.repositoryUrl=repositoryUrl.getText().toString().trim();
        config.baseBranch=baseBranch.getText().toString().trim();
        config.featureBranch=featureBranch.getText().toString().trim();
        config.authorName=authorName.getText().toString().trim();
        config.authorEmail=authorEmail.getText().toString().trim();
    }
    private void showGit() {
        LinearLayout body=page("Git Freedom Bridge");
        label(body,"Local-first repository workflow. Commits and normal pushes target the selected feature branch only.\\n" + GitFreedomBridge.compatibilityCheckpoint() + "\\nShared within the CodEXgen app process; each remote action still requires an unlocked token and explicit user action.");
        repositoryUrl=field(body,"HTTPS repository URL","https://github.com/Vanellye/CodEXgen.git",InputType.TYPE_CLASS_TEXT);
        baseBranch=field(body,"Base branch","main-11-of-38",InputType.TYPE_CLASS_TEXT);
        featureBranch=field(body,"Feature branch","olpirt/stride-next",InputType.TYPE_CLASS_TEXT);
        authorName=field(body,"Commit author","CodEXgen Contributor",InputType.TYPE_CLASS_TEXT);
        authorEmail=field(body,"Commit email","",InputType.TYPE_TEXT_VARIATION_EMAIL_ADDRESS);
        tokenField=field(body,"Fine-grained GitHub token","",InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_PASSWORD);
        vaultPass=field(body,"Vault passphrase (12+ characters)","",InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_PASSWORD);
        gitStatus=new TextView(this);
        gitStatus.setText("Local repository: "+git.localPath()+"\nRemote HTTPS transport requires Android API 21 or newer.");
        body.addView(gitStatus);
        localFilePath=field(body,"New repository-relative file path","notes/stride-session.txt",InputType.TYPE_CLASS_TEXT);
        localFileContents=new EditText(this);
        localFileContents.setHint("File contents to save in the local repository");
        localFileContents.setMinLines(4);
        localFileContents.setGravity(Gravity.TOP);
        localFileContents.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_FLAG_MULTI_LINE);
        body.addView(localFileContents,new LinearLayout.LayoutParams(-1,dp(120)));
        button(body,"Write file into local repository",new View.OnClickListener(){
            public void onClick(View v){
                final String path=localFilePath.getText().toString();
                final String contents=localFileContents.getText().toString();
                runWork(gitStatus,new Work(){public String run() throws Exception{return git.writeLocalFile(path,contents);}});
            }
        });
        button(body,"Save encrypted token",new View.OnClickListener(){
            public void onClick(View v){
                try{
                    git.saveToken(tokenField.getText().toString(),vaultPass.getText().toString().toCharArray());
                    tokenField.setText("");
                    vaultPass.setText("");
                    gitStatus.setText("Token encrypted with a passphrase-derived key. Passphrase is not stored.");
                }catch(Exception e){gitStatus.setText(e.getMessage());}
            }
        });
        button(body,"Unlock saved token for this session",new View.OnClickListener(){
            public void onClick(View v){
                try{
                    git.unlockToken(vaultPass.getText().toString().toCharArray());
                    vaultPass.setText("");
                    gitStatus.setText("Token unlocked in memory for this session.");
                }catch(Exception e){gitStatus.setText(e.getMessage());}
            }
        });
        button(body,"Initialize local repository",new View.OnClickListener(){
            public void onClick(View v){
                readConfig();
                runWork(gitStatus,new Work(){public String run() throws Exception{return git.initializeLocal(config);}});
            }
        });
        button(body,"Import workspace folder (Android API 21+)",new View.OnClickListener(){
            public void onClick(View v){
                if (android.os.Build.VERSION.SDK_INT < 21) {
                    gitStatus.setText("Folder import requires API 21+. Use the in-app text-file editor on API 11-20.");
                    return;
                }
                Intent picker = new Intent("android.intent.action.OPEN_DOCUMENT_TREE");
                picker.addFlags(1 | 2 | 64);
                startActivityForResult(picker, REQUEST_WORKSPACE_TREE);
            }
        });
        button(body,"Clone / prepare feature branch (API 21+ HTTPS)",new View.OnClickListener(){
            public void onClick(View v){
                readConfig();
                runWork(gitStatus,new Work(){public String run() throws Exception{return git.cloneOrPrepare(config);}});
            }
        });
        button(body,"Fetch feature branch",new View.OnClickListener(){
            public void onClick(View v){
                readConfig();
                runWork(gitStatus,new Work(){public String run() throws Exception{return git.fetch(config);}});
            }
        });
        button(body,"Pull feature branch (fast-forward only)",new View.OnClickListener(){
            public void onClick(View v){
                readConfig();
                runWork(gitStatus,new Work(){public String run() throws Exception{return git.pullFastForward(config);}});
            }
        });
        button(body,"Refresh changed-file review",new View.OnClickListener(){
            public void onClick(View v){
                readConfig();
                runWork(gitStatus,new Work(){public String run() throws Exception{
                    final List<String> paths=git.review(config);
                    runOnUiThread(new Runnable(){public void run(){populateChecks(paths);}});
                    return "Loaded "+paths.size()+" changed paths. Select the files to commit.";
                }});
            }
        });
        label(body,"Changed files — select exactly what to commit");
        changedFiles=new LinearLayout(this);
        changedFiles.setOrientation(LinearLayout.VERTICAL);
        body.addView(changedFiles);
        commitMessage=field(body,"Commit message","CodEXgen: reviewed feature update",InputType.TYPE_CLASS_TEXT);
        button(body,"Commit selected files locally",new View.OnClickListener(){
            public void onClick(View v){
                readConfig();
                final List<String> paths=selectedPaths();
                final String msg=commitMessage.getText().toString();
                runWork(gitStatus,new Work(){public String run() throws Exception{return git.commitSelected(config,paths,msg);}});
            }
        });
        button(body,"Push feature branch (normal push only)",new View.OnClickListener(){
            public void onClick(View v){
                readConfig();
                runWork(gitStatus,new Work(){public String run() throws Exception{return git.pushNormal(config);}});
            }
        });
        prTitle=field(body,"Draft pull request title","CodEXgen API 11 Views compatibility",InputType.TYPE_CLASS_TEXT);
        prBody=new EditText(this);
        prBody.setHint("Draft pull request description");
        prBody.setMinLines(3);
        prBody.setGravity(Gravity.TOP);
        body.addView(prBody,new LinearLayout.LayoutParams(-1,dp(100)));
        button(body,"Create / find draft pull request",new View.OnClickListener(){
            public void onClick(View v){
                readConfig();
                final String title=prTitle.getText().toString();
                final String description=prBody.getText().toString();
                runWork(gitStatus,new Work(){public String run() throws Exception{return git.createDraftPullRequest(config,title,description);}});
            }
        });
        button(body,"Clear saved token",new View.OnClickListener(){
            public void onClick(View v){git.clearToken();gitStatus.setText("Encrypted token removed.");}
        });
        label(body,"Safety: no force-push, no automatic base-branch merge, no destructive reset. API 11-15 can use local repository operations; remote HTTPS is gated.");
    }
    private void populateChecks(List<String> paths) {
        changedFiles.removeAllViews(); fileChecks.clear();
        for(int i=0;i<paths.size();i++){
            String path=paths.get(i);
            CheckBox c=new CheckBox(this); c.setText(path); c.setChecked(true);
            changedFiles.addView(c); fileChecks.put(path,c);
        }
    }
    private List<String> selectedPaths() {
        List<String> paths=new ArrayList<String>();
        for(Map.Entry<String,CheckBox> e:fileChecks.entrySet()) if(e.getValue().isChecked()) paths.add(e.getKey());
        return paths;
    }

    private void showResonance() {
        LinearLayout body=page("Data Resonance");
        label(body,"Local SQLite observation notebook. Frequency and biomarker labels are metadata, not biological modulation.");
        channelField=field(body,"Channel","signal-a",InputType.TYPE_CLASS_TEXT);
        valueField=field(body,"Measured value","",InputType.TYPE_CLASS_NUMBER | InputType.TYPE_NUMBER_FLAG_DECIMAL | InputType.TYPE_NUMBER_FLAG_SIGNED);
        unitField=field(body,"Unit","",InputType.TYPE_CLASS_TEXT);
        biomarkerField=field(body,"Biomarker label (optional)","",InputType.TYPE_CLASS_TEXT);
        frequencyField=field(body,"Reference frequency in Hz","11",InputType.TYPE_CLASS_NUMBER | InputType.TYPE_NUMBER_FLAG_DECIMAL);
        notesField=field(body,"Notes","",InputType.TYPE_CLASS_TEXT);
        final TextView result=new TextView(this);
        body.addView(result);
        button(body,"Save local observation",new View.OnClickListener(){
            public void onClick(View v){
                try{
                    double value=Double.parseDouble(valueField.getText().toString());
                    String f=frequencyField.getText().toString().trim();
                    Double hz=f.length()==0?null:Double.valueOf(Double.parseDouble(f));
                    long id=data.add(channelField.getText().toString(),value,unitField.getText().toString(),
                        biomarkerField.getText().toString(),hz,notesField.getText().toString());
                    result.setText("Saved observation #"+id+" to app-private SQLite.");
                    valueField.setText(""); notesField.setText("");
                }catch(Exception e){result.setText("Save failed: "+e.getMessage());}
            }
        });
        correlationA=field(body,"Correlation channel A","signal-a",InputType.TYPE_CLASS_TEXT);
        correlationB=field(body,"Correlation channel B","signal-b",InputType.TYPE_CLASS_TEXT);
        button(body,"Calculate exploratory Pearson r",new View.OnClickListener(){
            public void onClick(View v){
                try{
                    DataResonanceStore.Correlation c=data.correlation(
                        correlationA.getText().toString(),correlationB.getText().toString());
                    result.setText("Matched samples: "+c.sampleCount+"\\nPearson r: "+
                        (c.pearsonR == null ? "not available" : String.valueOf(c.pearsonR.doubleValue()))+
                        "\\nDescriptive association only; not causal or clinical evidence.");
                }catch(Exception e){result.setText("Correlation failed: "+e.getMessage());}
            }
        });
        button(body,"Show recent observations",new View.OnClickListener(){
            public void onClick(View v){result.setText(data.recent(100));}
        });
        label(body,"Database is local to this app. Back up deliberately before uninstalling.");
    }


    private void showConsent() {
        LinearLayout body = page("Stride Consent & Human Review");
        label(body, "A supportive pause—not a test of character, faith, intelligence, or worth. Do not continue if any essential point is unclear. A checked item records that it was explained and understood; it does not prove understanding.");
        label(body, "Proposed purpose / action");
        final EditText purpose = new EditText(this);
        purpose.setHint("Describe what is proposed, why, and who may be affected");
        purpose.setMinLines(3);
        purpose.setGravity(Gravity.TOP);
        purpose.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_FLAG_MULTI_LINE);
        body.addView(purpose, new LinearLayout.LayoutParams(-1, dp(96)));

        final String[] layerText = new String[]{
            "1. Safety and dignity — the person can pause or leave without penalty; immediate safety needs and support options were discussed.",
            "2. Purpose and meaning — the proposal and its reason were explained in plain language; questions were welcomed.",
            "3. Evidence and uncertainty — facts, interpretations, unknowns, sources, and alternatives were distinguished.",
            "4. Consequences and boundaries — material benefits, risks, data use, affected people, and limits were explained.",
            "5. Freedom from pressure — no threats, shame, retaliation, authority pressure, peer pressure, or artificial urgency is being used.",
            "6. Choice and reversibility — the person can decline, ask for time or advice, and understands withdrawal and next steps.",
            "7. Human accountability — a responsible human reviewer is identified and can answer questions and oversee the decision."
        };
        final CheckBox[] layers = new CheckBox[7];
        for (int i = 0; i < layerText.length; i++) {
            layers[i] = new CheckBox(this);
            layers[i].setText(layerText[i]);
            layers[i].setPadding(0, dp(5), 0, dp(5));
            body.addView(layers[i], new LinearLayout.LayoutParams(-1, -2));
        }

        label(body, "Human reviewer (required before recording assent)");
        final EditText reviewer = field(body, "Name or role of accountable human reviewer", "", InputType.TYPE_CLASS_TEXT);
        final CheckBox reviewerConfirmed = new CheckBox(this);
        reviewerConfirmed.setText("I am the designated human reviewer; I have reviewed the proposal, checked for pressure or unresolved concerns, and remain accountable for follow-up.");
        body.addView(reviewerConfirmed, new LinearLayout.LayoutParams(-1, -2));

        final CheckBox voluntaryChoice = new CheckBox(this);
        voluntaryChoice.setText("I have had a genuine opportunity to ask questions and freely choose to proceed. I understand I can say no.");
        body.addView(voluntaryChoice, new LinearLayout.LayoutParams(-1, -2));

        // Any change to reviewed material invalidates an earlier assent click.
        for (int i = 0; i < layers.length; i++) {
            layers[i].setOnCheckedChangeListener(new android.widget.CompoundButton.OnCheckedChangeListener() {
                public void onCheckedChanged(android.widget.CompoundButton buttonView, boolean isChecked) {
                    voluntaryChoice.setChecked(false);
                }
            });
        }
        reviewerConfirmed.setOnCheckedChangeListener(new android.widget.CompoundButton.OnCheckedChangeListener() {
            public void onCheckedChanged(android.widget.CompoundButton buttonView, boolean isChecked) {
                voluntaryChoice.setChecked(false);
            }
        });
        TextWatcher invalidateChoice = new TextWatcher() {
            public void beforeTextChanged(CharSequence s, int start, int count, int after) { }
            public void onTextChanged(CharSequence s, int start, int before, int count) { voluntaryChoice.setChecked(false); }
            public void afterTextChanged(Editable e) { }
        };
        purpose.addTextChangedListener(invalidateChoice);
        reviewer.addTextChangedListener(invalidateChoice);

        final TextView state = new TextView(this);
        state.setText("Status: PAUSED — no assent has been recorded.");
        state.setPadding(0, dp(10), 0, dp(10));
        body.addView(state);

        button(body, "Record voluntary assent (all safeguards required)", new View.OnClickListener() {
            public void onClick(View v) {
                boolean[] flags = new boolean[7];
                boolean complete = true;
                for (int i = 0; i < 7; i++) {
                    flags[i] = layers[i].isChecked();
                    if (!flags[i]) complete = false;
                }
                if (!complete) {
                    state.setText("PAUSED — explain and resolve every layer before asking for assent.");
                    return;
                }
                if (purpose.getText().toString().trim().length() == 0) {
                    state.setText("PAUSED — describe the purpose and proposed action first.");
                    return;
                }
                if (reviewer.getText().toString().trim().length() == 0 || !reviewerConfirmed.isChecked()) {
                    state.setText("PAUSED — an accountable human reviewer must review and confirm.");
                    return;
                }
                if (!voluntaryChoice.isChecked()) {
                    state.setText("NO ASSENT — the person's voluntary choice has not been given. They may pause or decline.");
                    return;
                }
                long id = consentReviews.record("ASSENTED", flags, reviewer.getText().toString(), purpose.getText().toString());
                state.setText("ASSENT RECORDED locally as review #" + id + ". This record is not a legal determination and does not authorize unrelated actions.");
                voluntaryChoice.setChecked(false);
            }
        });
        button(body, "Record decline — no penalty", new View.OnClickListener() {
            public void onClick(View v) {
                long id = consentReviews.record("DECLINED", layerFlags(layers), "", purpose.getText().toString());
                voluntaryChoice.setChecked(false);
                state.setText("DECLINED — review #" + id + " recorded locally. No assent was given.");
            }
        });
        button(body, "Pause / request more explanation", new View.OnClickListener() {
            public void onClick(View v) {
                long id = consentReviews.record("PAUSED", layerFlags(layers), reviewer.getText().toString(), purpose.getText().toString());
                voluntaryChoice.setChecked(false);
                state.setText("PAUSED — review #" + id + " recorded. No assent was given; revisit only if the person chooses.");
            }
        });
        button(body, "Show local review history", new View.OnClickListener() {
            public void onClick(View v) { state.setText(consentReviews.recent(50)); }
        });
        label(body, "Privacy: review records are stored in app-private SQLite and are not encrypted by this prototype. Keep the purpose summary minimal; do not enter medical, child-protection, or other sensitive personal details.");
        label(body, "Safeguards: no readiness score; no inferred consent from silence, clicks, or continued use; no forced assent. Youth cases require age-appropriate explanation and applicable guardian/safeguarding processes, while respecting the young person's questions and dissent. This screen does not replace legal, clinical, or child-protection review.");
    }

    private boolean[] layerFlags(CheckBox[] checks) {
        boolean[] flags = new boolean[7];
        for (int i = 0; i < 7; i++) flags[i] = checks[i].isChecked();
        return flags;
    }

    private void showOlpirt() {
        LinearLayout body=page("Olpirt / Pons Native Bridge");
        final TextView report=new TextView(this);
        report.setText(new OlpirtNativeBridge().status());
        report.setTextIsSelectable(true);
        body.addView(report);
        button(body,"Refresh native dependency report",new View.OnClickListener(){
            public void onClick(View v){report.setText(new OlpirtNativeBridge().status());}
        });
        label(body,"Native C++ bridge is built for armeabi-v7a / Android API 11 using C++11.");
    }

    protected void onActivityResult(int requestCode, int resultCode, Intent dataIntent) {
        super.onActivityResult(requestCode, resultCode, dataIntent);
        if (requestCode == REQUEST_WORKSPACE_TREE && resultCode == RESULT_OK && dataIntent != null) {
            final Uri treeUri = dataIntent.getData();
            runWork(gitStatus,new Work(){public String run() throws Exception{
                int copied = git.importWorkspaceTree(treeUri);
                return "Imported " + copied + " workspace files into the local feature repository.";
            }});
        }
    }

    protected void onDestroy() {
        if(data!=null) data.close();
        if(consentReviews!=null) consentReviews.close();
        super.onDestroy();
    }
}
