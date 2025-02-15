import { Route, Routes } from "react-router-dom";
import NavBar from "../../components/Navbar";
import { Home } from "../../pages/Home";
import Usuarios from "../../pages/Usuarios";

const Private = () => {
  return (
    <>
      <NavBar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/usuarios" element={<Usuarios />} />
      </Routes>
    </>
  );
};

export default Private;
