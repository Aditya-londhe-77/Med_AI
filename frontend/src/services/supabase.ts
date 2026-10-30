import { createClient } from '@supabase/supabase-js'

// We expect these to be injected by Vite's import.meta.env
// The user will need to create frontend/.env to store these.
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL || 'https://placeholder.supabase.co'
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || 'placeholder'

export const supabase = createClient(supabaseUrl, supabaseAnonKey)
