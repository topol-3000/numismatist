// Environment variable validation
export const validateEnvironment = () => {
  const requiredVars = ['VITE_API_URL'] as const

  const missing = requiredVars.filter((varName) => !import.meta.env[varName])

  if (missing.length > 0) {
    throw new Error(
      `Missing required environment variables: ${missing.join(', ')}\n` +
        'Please check your .env file and ensure all required variables are set.',
    )
  }
}

// Environment configuration with proper typing
export const env = {
  API_URL: import.meta.env.VITE_API_URL as string,
}

// Validate environment on module load
validateEnvironment()
