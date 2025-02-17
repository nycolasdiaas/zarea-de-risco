function Neighborhood() {
    return (
      <div className="container featured">
        <h1 className="Featured_MainTitle">Procure por bairros</h1>
          <div className="d-flex flex-wrap text-center justify-content-center">
            <div className="col-md col-sm featured_container">
              <img
                className="bairros bairros fadeInUp rounded-3"
                src="/imgs/Aerolandia.png"
                alt="Imagem"
              />
              
              {/* <div className="AnimatedText d-flex flex-wrap justify-content-center">
                <h3 className="featured_news_title">Aerolandia</h3>
              </div> */}
              <div className="AnimatedTextNeighboorhood d-flex flex-wrap justify-content-center ">
              <p className="featured_news_title_neighboorhood">Aerolandia</p>
            </div>
            </div>
  
            <div className="col-md col-sm featured_container">
              <img
                className="bairros fadeInUp rounded-3"
                src="/imgs/Cajazeiras.png"
                alt="Imagem"
              />
              <div className="AnimatedTextNeighboorhood d-flex flex-wrap justify-content-center">
                <h3 className="featured_news_title_neighboorhood">Cajazeiras</h3>
              </div>
            </div>
          
            <div className="col-md col-sm featured_container">
              <img
                className="bairros fadeInUp rounded-3"
                src="/imgs/Cambeba.png"
                alt="Imagem"
              />
          
              <div className="AnimatedTextNeighboorhood d-flex flex-wrap justify-content-center">
                <h3 className="featured_news_title_neighboorhood">Cambeba</h3>
              </div>
            </div>
            <div className="col-md col-sm featured_container">
              <img
                className="bairros fadeInUp rounded-3"
                src="/imgs/Edson_Queiroz.png"
                alt="Imagem"
              />
              <div className="AnimatedTextNeighboorhood d-flex flex-wrap justify-content-center">
                <h3 className="featured_news_title_neighboorhood">Edson Queiroz</h3>
              </div>
            </div>

            <div className="col-md col-sm featured_container">
              <img
                className="bairros fadeInUp rounded-3"
                src="/imgs/Jose_de_Alencar.png"
                alt="Imagem"
              />
              <div className="AnimatedTextNeighboorhood d-flex flex-wrap justify-content-center">
                <h3 className="featured_news_title_neighboorhood">Jose de Alencar</h3>
              </div>
            </div>

            <div className="col-md col-sm featured_container">
              <img
                className="bairros fadeInUp rounded-3"
                src="/imgs/Lagoa_Sapiranga.png"
                alt="Imagem"
              />
              <div className="AnimatedTextNeighboorhood d-flex flex-wrap justify-content-center">
                <h3 className="featured_news_title_neighboorhood">Lagoa Sapiranga</h3>
              </div>
            </div>

            <div className="col-md col-sm featured_container">
              <img
                className="bairros fadeInUp rounded-3"
                src="/imgs/Parque_Iracema.png"
                alt="Imagem"
              />
              <div className="AnimatedTextNeighboorhood d-flex flex-wrap justify-content-center">
                <h3 className="featured_news_title_neighboorhood">Parque Iracema</h3>
              </div>
            </div>
            
          </div>
          <div className="row justify-content-center">
            <button className="btn btn-simple col-1" type="button">
              Ver Mais
            </button>
          </div>
      </div>
    );
  }
  
  export default Neighborhood;
  