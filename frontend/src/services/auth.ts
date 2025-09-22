// Simple authentication service for demo purposes
// In production, this would connect to a proper auth service

export interface AuthToken {
  token: string;
  expiresAt: number;
}

class AuthService {
  private static instance: AuthService;
  private token: AuthToken | null = null;

  private constructor() {}

  static getInstance(): AuthService {
    if (!AuthService.instance) {
      AuthService.instance = new AuthService();
    }
    return AuthService.instance;
  }

  // For demo purposes, generate a test token
  async getTestToken(): Promise<string> {
    // This would normally be obtained from a login endpoint
    // For demo, we'll use a hardcoded test token
    const testToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJvZmZpY2VyX2lkIjoidGVzdF9vZmZpY2VyXzAwMSIsInJvbGUiOiJhbmFseXN0IiwicGVybWlzc2lvbnMiOlsibmxwOmFuYWx5emUiLCJubHA6c2VudGltZW50IiwiYWRtaW46bW9kZWxzIiwibmxwOnN0YXRzIl0sImV4cCI6MTc1ODU4OTU1MSwiaWF0IjoxNzU4NTAzMTUxLCJtZmFfdmVyaWZpZWQiOnRydWV9.MOUWql97zxY_UrfLD_ipevNCir_k81owuEDCdCnVHac';
    
    this.token = {
      token: testToken,
      expiresAt: Date.now() + 24 * 60 * 60 * 1000 // 24 hours
    };

    return testToken;
  }

  async getValidToken(): Promise<string | null> {
    if (!this.token || Date.now() > this.token.expiresAt) {
      // Token expired or doesn't exist, get a new one
      try {
        return await this.getTestToken();
      } catch (error) {
        console.error('Failed to get auth token:', error);
        return null;
      }
    }
    return this.token.token;
  }

  clearToken(): void {
    this.token = null;
  }
}

export default AuthService.getInstance();