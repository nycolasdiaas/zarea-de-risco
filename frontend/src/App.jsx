import "./app.scss"
import "./index.css"
import Navbar from "./components/Navbar"
import Featured from "./components/Featured"
import Neighborhood from "./components/Neighborhood"
// import { useEffect, useState } from "react"
// import apiService from "./services/apiService"


function App() {
  // const [dados, setDados] = useState([])
  // const [error, setError] = useState(null)

  // useEffect(() => {
  //   const fetchDados = async () => {
  //     try {
  //       const response = await apiService.getMetadataFromDate("2025-01-17")
  //       setDados(response.data)
  //     } catch (error) {
  //       setError(error.message)
  //     }
  //   }

  //   fetchDados()
  // }, [])

  return (
    <>
      <div>
        <Navbar/>
        <Featured />
        <Neighborhood />
      </div>
      {/* <div>
        <h1>Dados do MinIO</h1>
        {error ? (
          <p style={{ color: "red" }}>Erro: {error}</p>
        ) : (
          <p>
            {JSON.stringify(dados, null, 2)}
          </p>
        )}
      </div> */}
    </>
  )
}

export default App