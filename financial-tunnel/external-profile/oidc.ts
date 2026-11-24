import { createRemoteJWKSet, jwtVerify } from "jose";
import type { ExternalIdentity } from "./contracts.ts";

export interface OidcVerifier { verify(token: string): Promise<ExternalIdentity>; }

export function createOidcVerifier(env: NodeJS.ProcessEnv = process.env): OidcVerifier {
  const issuer = env.OIDC_ISSUER;
  const audience = env.OIDC_AUDIENCE;
  const jwksUrl = env.OIDC_JWKS_URL;
  if (!issuer || !audience || !jwksUrl) {
    throw new Error("OIDC_ISSUER, OIDC_AUDIENCE and OIDC_JWKS_URL are required.");
  }
  const jwks = createRemoteJWKSet(new URL(jwksUrl));
  return {
    async verify(token) {
      const { payload } = await jwtVerify(token, jwks, {
        issuer, audience, algorithms: ["RS256", "ES256"],
      });
      if (typeof payload.sub !== "string" || typeof payload.iss !== "string") {
        throw new Error("OIDC token is missing required issuer or subject claims.");
      }
      return {
        issuer: payload.iss, subject: payload.sub,
        email: typeof payload.email === "string" ? payload.email : undefined,
        displayName: typeof payload.name === "string" ? payload.name : undefined,
      };
    },
  };
}
