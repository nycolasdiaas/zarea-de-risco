import Links from "../Links";
import Logo from "../Logo";
import SearchBar from "../SearchBar/index.jsx";

function Navbar() {
  return (
      <nav id="navbar" className="navbar navbar-expand-lg sticky-top">
        <div className="container-fluid d-flex">
          <Logo />
          <div className="justify-content-start">
          <a className="navbar-brand" href="#" id="navbarTitle">Zarea de Risco</a>
          </div>
          <Links />
          <SearchBar />
        </div>
      </nav>
  );
}

export default Navbar;
