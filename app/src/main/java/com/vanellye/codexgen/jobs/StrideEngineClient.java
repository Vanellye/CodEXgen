package com.vanellye.codexgen.jobs;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import org.json.JSONObject;

/** Explicit, authenticated HTTP adapter to a separately running Stride Python bridge. */
public final class StrideEngineClient {
    private final String endpoint;
    private final String token;
    public StrideEngineClient(String endpoint, String token) {
        if (endpoint == null || token == null || token.trim().length() == 0)
            throw new IllegalArgumentException("Bridge URL and bearer token are required.");
        String value=endpoint.trim();
        boolean local=value.startsWith("http://localhost:") || value.startsWith("http://127.0.0.1:");
        if (!value.startsWith("https://") && !local)
            throw new IllegalArgumentException("Use HTTPS for remote bridges; cleartext is allowed only for localhost.");
        while(value.endsWith("/")) value=value.substring(0,value.length()-1);
        this.endpoint=value; this.token=token.trim();
    }
    public JSONObject runFaculty(String jobId, JSONObject payload) throws Exception {
        return request("POST","/v1/jobs/"+jobId+"/faculty",payload);
    }
    public JSONObject attachGeometry(String jobId, JSONObject experiment) throws Exception {
        return request("POST","/v1/jobs/"+jobId+"/geometry",experiment);
    }
    public JSONObject listArtifacts(String jobId) throws Exception {
        return request("GET","/v1/jobs/"+jobId+"/artifacts",null);
    }
    private JSONObject request(String method,String path,JSONObject payload) throws Exception {
        HttpURLConnection c=null;
        try {
            URL url=new URL(endpoint+path); c=(HttpURLConnection)url.openConnection();
            c.setRequestMethod(method); c.setConnectTimeout(8000); c.setReadTimeout(15000);
            c.setRequestProperty("Accept","application/json");
            c.setRequestProperty("Authorization","Bearer "+token);
            if(payload!=null) {
                byte[] bytes=payload.toString().getBytes("UTF-8");
                if(bytes.length>2097152) throw new IllegalArgumentException("Request exceeds 2 MB.");
                c.setDoOutput(true); c.setRequestProperty("Content-Type","application/json; charset=utf-8");
                c.setFixedLengthStreamingMode(bytes.length);
                OutputStream out=c.getOutputStream();
                try { out.write(bytes); } finally { out.close(); }
            }
            int code=c.getResponseCode();
            InputStream in=(code>=200 && code<400)?c.getInputStream():c.getErrorStream();
            ByteArrayOutputStream buffer=new ByteArrayOutputStream();
            if(in!=null) {
                try {
                    byte[] chunk=new byte[4096]; int n; int total=0;
                    while((n=in.read(chunk))!=-1) {
                        total+=n; if(total>2097152) throw new IllegalStateException("Bridge response exceeds 2 MB.");
                        buffer.write(chunk,0,n);
                    }
                } finally { in.close(); }
            }
            String text=new String(buffer.toByteArray(),"UTF-8");
            JSONObject result=text.length()==0?new JSONObject():new JSONObject(text);
            if(code<200 || code>=300) throw new IllegalStateException("Stride bridge HTTP "+code+": "+result.optString("error",text));
            return result;
        } finally { if(c!=null)c.disconnect(); }
    }
}
