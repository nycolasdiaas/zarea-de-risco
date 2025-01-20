function Featured() {
  return (
    <div className="container featured">
      <h1 className="Featured_MainTitle">Fique por dentro do que está acontecendo nos bairros de fortaleza</h1>
      <div className="row justify-content-center">
        <div className="d-flex flex-wrap justify-content-center text-center">
          <div className="col-md col-sm featured_container">
            <img
              className="animatable fadeInUp rounded-3"
              src="/imgs/test1.png"
              alt="Imagem"
            />
            
            <div className="AnimatedText">
              <h3 className="featured_news_title">Taxista morto em casa no Parque Araxá</h3>
              <p className="featured_normal_text">baleado na cabeça dentro de casa ao tentar reagir a um assalto</p>
            </div>
          </div>

          <div className="col-md col-sm featured_container">
            <img
              className="animatable fadeInUp rounded-3"
              src="/imgs/test2.png"
              alt="Imagem"
            />
            <div className="AnimatedText">
              <h3 className="featured_main_title">Taxista morto em casa no Parque Araxá</h3>
              <p className="featured_normal_text">dezenas de pessoas aplicando socos, chutes e golpes com capacete contra os suspeitos.</p>
            </div>
          </div>
        
          <div className="col-md col-sm featured_container">
            <img
              className="animatable fadeInUp rounded-3"
              src="/imgs/test3.jpg"
              alt="Imagem"
            />
        
            <div className="AnimatedText">
              <h3 className="featured_main_title">Taxista morto em casa no Parque Araxá</h3>
              <p className="featured_normal_text">baleado na cabeça dentro de casa ao tentar reagir a um assalto</p>
            </div>
          </div>
          
        </div>
        <button className="">click me</button>
      </div>
    </div>
  );
}

export default Featured;
