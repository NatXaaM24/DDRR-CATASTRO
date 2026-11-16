export type Rol = 'funcionario' | 'encargado'

export interface Usuario {
  id: string
  username: string
  nombre_completo: string
  rol: Rol
}

// Respuesta del paso 1 (contraseña): todavía no hay sesión.
export interface LoginSalida {
  preauth_token: string
  token_type: string
  expires_in: number
  tiene_credencial: boolean
}

// Respuesta cuando contraseña y biometría ya fueron verificadas.
export interface TokenSalida {
  access_token: string
  token_type: string
  expires_in: number
  usuario: Usuario
}
