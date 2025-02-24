function RecentNews() {
    return (
      <div className="container featured" id="RecentesSection">
      <h1 className="Featured_MainTitle">Fique por dentro do que está acontecendo nos bairros de fortaleza</h1>
        <div className="row d-flex flex-wrap text-center justify-content-center">
          <div className="col-md col-sm featured_container">
            <img
              className="fadeInUp rounded-3"
              src="/imgs/test1.png"
              alt="Imagem"
            />
            
            <div className="AnimatedText d-flex flex-wrap justify-content-center">
              <h3 className="featured_news_title">Taxista morto em casa no Parque Araxá</h3>
              <p className="featured_normal_text">baleado na cabeça dentro de casa ao tentar reagir a um assalto</p>
            </div>
          </div>

          <div className="col-md col-sm featured_container">
            <img
              className="fadeInUp rounded-3"
              src="/imgs/test2.png"
              alt="Imagem"
            />
            
            <div className="AnimatedText d-flex flex-wrap justify-content-center">
              <h3 className="featured_news_title">Suspeitos de assalto são agredidos</h3>
              <p className="featured_normal_text">dezenas de pessoas aplicando socos, chutes e golpes com capacete contra os suspeitos.</p>
            </div>
          </div>
        
          <div className="col-md col-sm featured_container">
            <img
              className="fadeInUp rounded-3"
              src="/imgs/test3.jpg"
              alt="Imagem"
            />
            
            <div className="AnimatedText d-flex flex-wrap justify-content-center">
              <h3 className="featured_news_title">Guarda-costas do Gus procura W.W.</h3>
              <p className="featured_normal_text">Ele permanece enfurecido depois dos ocorridos</p>
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
  
  export default RecentNews;
  