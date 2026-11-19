import { Navigate, Route, Routes } from 'react-router'
import { DisenoApp } from './components/DisenoApp'
import { LoginPage } from './features/auth/LoginPage'
import { RutaProtegida } from './features/auth/RutaProtegida'
import { PaginaInicio } from './features/auth/inicio/PaginaInicio'
import { PaginaDocumentos } from './features/documentos/PaginaDocumentos'
import { VisorDocumento } from './features/documentos/VisorDocumento'

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<RutaProtegida />}>
        <Route element={<DisenoApp />}>
          <Route path="/" element={<PaginaInicio />} />
          <Route path="/documentos" element={<PaginaDocumentos />} />
          <Route path="/documentos/:id" element={<VisorDocumento />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
