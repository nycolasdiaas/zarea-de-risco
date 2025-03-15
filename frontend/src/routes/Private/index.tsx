import React from "react";
import { Route, Routes } from "react-router-dom";
import NavBar from "../../components/Navbar";
import Home  from "../../pages/Home";
import News from "../../pages/AboutNews";

const Private = () => {
  return (
    <>
      <NavBar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/noticia" element={<News />} />
      </Routes>
    </>
  );
};

export default Private;
