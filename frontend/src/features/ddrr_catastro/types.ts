export interface Partida {
  id: string
  matricula: string
  titular_nombre: string
  titular_ci: string
  superficie_m2: string
  direccion: string
  codigo_catastral: string
  fecha_inscripcion: string
}

export interface PoligonoGeoJson {
  type: 'Polygon'
  coordinates: [number, number][][]
}

export interface Predio {
  id: string
  codigo_catastral: string
  propietario_nombre: string
  propietario_ci: string
  superficie_m2: string
  direccion: string
  distrito: string
  geometria: PoligonoGeoJson
}
