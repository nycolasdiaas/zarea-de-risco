import Container from "react-bootstrap/Container";
import Navbar from "react-bootstrap/Navbar";

function NavBar() {
  return (
    <Navbar sticky="top" className="bg-body-tertiary testing">
      <Container fluid>
        <Navbar.Brand href="#home">
          <img
            alt=""
            src="../../../public/imgs/AZAREA2 1.png"
            width="30"
            height="30"
            className="d-inline-block align-top"
          />{" "}
          React Bootstrap
        </Navbar.Brand>
      </Container>
    </Navbar>
  );
}

export default NavBar;
