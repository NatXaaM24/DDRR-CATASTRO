import { Navigate, Route, Routes } from 'react-router'
import { LoginPage } from './features/auth/LoginPage'
import { RutaProtegida } from './features/auth/RutaProtegida'
import { PaginaInicio } from './features/auth/inicio/PaginaInicio'
import { PaginaDocumentos } from './features/documentos/PaginaDocumentos'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<RutaProtegida />}>
        <Route path="/" element={<PaginaInicio />} />
        <Route path="/documentos" element={<PaginaDocumentos />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
