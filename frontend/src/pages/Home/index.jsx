import Featured from "../../components/Featured"
import Neighborhood from "../../components/Neighborhood"
import RecentNews from "../../components/RecentNews"
import Footer from "../../components/Footer"
import Navbar from "../../components/Navbar";

function Home() {
  return (
    <>
      <div>
        <Navbar />
        <Featured />
        <Neighborhood />
        <RecentNews />
        <Footer />
      </div>
    </>
  );
}

export default Home;
