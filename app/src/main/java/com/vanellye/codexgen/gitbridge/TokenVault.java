package com.vanellye.codexgen.gitbridge;

import android.content.Context;
import android.content.SharedPreferences;
import android.util.Base64;
import java.security.MessageDigest;
import java.security.SecureRandom;
import javax.crypto.Cipher;
import javax.crypto.Mac;
import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.IvParameterSpec;
import javax.crypto.spec.PBEKeySpec;
import javax.crypto.spec.SecretKeySpec;

/** API-11-compatible encrypted token vault. The user passphrase is never persisted. */
public final class TokenVault {
    private final SharedPreferences prefs;
    public TokenVault(Context context) {
        prefs = context.getApplicationContext().getSharedPreferences("git_bridge_vault_v1", Context.MODE_PRIVATE);
    }
    private byte[] derive(char[] pass, byte[] salt) throws Exception {
        PBEKeySpec spec = new PBEKeySpec(pass, salt, 100000, 256);
        try {
            return SecretKeyFactory.getInstance("PBKDF2WithHmacSHA1").generateSecret(spec).getEncoded();
        } finally { spec.clearPassword(); }
    }
    private byte[] mac(byte[] key, byte[] salt, byte[] iv, byte[] data) throws Exception {
        byte[] all = new byte[salt.length + iv.length + data.length];
        System.arraycopy(salt, 0, all, 0, salt.length);
        System.arraycopy(iv, 0, all, salt.length, iv.length);
        System.arraycopy(data, 0, all, salt.length + iv.length, data.length);
        Mac m = Mac.getInstance("HmacSHA256");
        m.init(new SecretKeySpec(key, "HmacSHA256"));
        return m.doFinal(all);
    }
    public void save(String token, char[] passphrase) throws Exception {
        if (token == null || token.length() == 0) throw new IllegalArgumentException("Token is required.");
        if (passphrase == null || passphrase.length < 12) throw new IllegalArgumentException("Vault passphrase must be at least 12 characters.");
        byte[] salt = new byte[16], iv = new byte[16];
        SecureRandom random = new SecureRandom();
        random.nextBytes(salt); random.nextBytes(iv);
        byte[] keys = derive(passphrase, salt);
        byte[] aes = new byte[16], hmac = new byte[16];
        System.arraycopy(keys, 0, aes, 0, 16);
        System.arraycopy(keys, 16, hmac, 0, 16);
        Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
        cipher.init(Cipher.ENCRYPT_MODE, new SecretKeySpec(aes, "AES"), new IvParameterSpec(iv));
        byte[] encrypted = cipher.doFinal(token.getBytes("UTF-8"));
        byte[] tag = mac(hmac, salt, iv, encrypted);
        SharedPreferences.Editor e = prefs.edit();
        e.putString("salt", Base64.encodeToString(salt, Base64.NO_WRAP));
        e.putString("iv", Base64.encodeToString(iv, Base64.NO_WRAP));
        e.putString("data", Base64.encodeToString(encrypted, Base64.NO_WRAP));
        e.putString("mac", Base64.encodeToString(tag, Base64.NO_WRAP));
        if (!e.commit()) throw new IllegalStateException("Could not persist encrypted token.");
    }
    public String read(char[] passphrase) throws Exception {
        String s = prefs.getString("salt", null), v = prefs.getString("iv", null);
        String d = prefs.getString("data", null), m = prefs.getString("mac", null);
        if (s == null || v == null || d == null || m == null) return null;
        if (passphrase == null || passphrase.length < 8) throw new IllegalArgumentException("Enter the vault passphrase.");
        byte[] salt = Base64.decode(s, Base64.NO_WRAP);
        byte[] iv = Base64.decode(v, Base64.NO_WRAP);
        byte[] encrypted = Base64.decode(d, Base64.NO_WRAP);
        byte[] supplied = Base64.decode(m, Base64.NO_WRAP);
        byte[] keys = derive(passphrase, salt);
        byte[] aes = new byte[16], hmac = new byte[16];
        System.arraycopy(keys, 0, aes, 0, 16);
        System.arraycopy(keys, 16, hmac, 0, 16);
        byte[] expected = mac(hmac, salt, iv, encrypted);
        if (!MessageDigest.isEqual(expected, supplied)) throw new SecurityException("Vault passphrase is incorrect or stored data was modified.");
        Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
        cipher.init(Cipher.DECRYPT_MODE, new SecretKeySpec(aes, "AES"), new IvParameterSpec(iv));
        return new String(cipher.doFinal(encrypted), "UTF-8");
    }
    public void clear() {
        prefs.edit().clear().commit();
    }
}
