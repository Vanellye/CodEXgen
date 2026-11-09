package com.vanellye.codexgen;

import android.app.Activity;
import android.os.Bundle;
import android.os.AsyncTask;
import android.view.View;
import android.view.Gravity;
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

/** Native Android Views application. No Compose, Kotlin, AndroidX or Lifecycle dependency. */
public final class MainActivity extends Activity {
    private LinearLayout root;
    private FrameLayout content;
    private GitFreedomBridge git;
    private DataResonanceStore data;
    private EditText repositoryUrl, baseBranch, featureBranch, authorName, authorEmail;
    private EditText tokenField, vaultPass, commitMessage;
    private EditText channelField, valueField, unitField, biomarkerField, frequencyField, notesField;
    private TextView gitStatus;
    private LinearLayout changedFiles;
    private final Map<String, CheckBox> fileChecks = new HashMap<String, CheckBox>();
    private GitFreedomBridge.Config config;

    private interface Work { String run() throws Exception; }

    public void onCreate(Bundle state) {
        super.onCreate(state);
        git = new GitFreedomBridge(this);
        data = new DataResonanceStore(this);
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
        String[] labels = new String[]{"CodeGen","Git","Resonance","Olpirt"};
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
                    else if(index==2) showResonance();
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
        label(body,"Local-first repository workflow. Commits and normal pushes target the selected feature branch only.");
        repositoryUrl=field(body,"HTTPS repository URL","https://github.com/Vanellye/CodEXgen.git",InputType.TYPE_CLASS_TEXT);
        baseBranch=field(body,"Base branch","main-11-of-38",InputType.TYPE_CLASS_TEXT);
        featureBranch=field(body,"Feature branch","olpirt/stride-next",InputType.TYPE_CLASS_TEXT);
        authorName=field(body,"Commit author","CodEXgen Contributor",InputType.TYPE_CLASS_TEXT);
        authorEmail=field(body,"Commit email","",InputType.TYPE_TEXT_VARIATION_EMAIL_ADDRESS);
        tokenField=field(body,"Fine-grained GitHub token","",InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_PASSWORD);
        vaultPass=field(body,"Vault passphrase (8+ characters)","",InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_PASSWORD);
        gitStatus=new TextView(this);
        gitStatus.setText("Local repository: "+git.localPath()+"\nRemote HTTPS transport is disabled on API 11-15.");
        body.addView(gitStatus);
        button(body,"Save encrypted token",new View.OnClickListener(){
            public void onClick(View v){
                try{
                    git.saveToken(tokenField.getText().toString(),vaultPass.getText().toString().toCharArray());
                    tokenField.setText("");
                    gitStatus.setText("Token encrypted with a passphrase-derived key. Passphrase is not stored.");
                }catch(Exception e){gitStatus.setText(e.getMessage());}
            }
        });
        button(body,"Unlock saved token for this session",new View.OnClickListener(){
            public void onClick(View v){
                try{
                    git.unlockToken(vaultPass.getText().toString().toCharArray());
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
        button(body,"Clone / prepare feature branch (API 16+ HTTPS)",new View.OnClickListener(){
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
        button(body,"Show recent observations",new View.OnClickListener(){
            public void onClick(View v){result.setText(data.recent(100));}
        });
        label(body,"Database is local to this app. Back up deliberately before uninstalling.");
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

    protected void onDestroy() {
        if(data!=null) data.close();
        super.onDestroy();
    }
}
