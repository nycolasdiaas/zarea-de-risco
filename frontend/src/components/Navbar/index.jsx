import Links from "../Links";
import Logo from "../Logo";

function Navbar() {
  return (
    <nav id="navbar" className="navbar navbar-expand-lg sticky-top">
      <div className="container-fluid d-flex">
        <Logo />
        <h2 className="text-sm-start">Zarea de Risco</h2>
        <Links />
      </div>
    </nav>
  );
}

export default Navbar;
