import { BrowserRouter as Router, Routes, Route } from "react-router";
import NotFound from "./pages/OtherPage/NotFound";
import ClusterList from "./pages/ClusterList/ClusterList";
import AddCluster from "./pages/AddCluster/AddCluster";
import AppLayout from "./layout/AppLayout";
import { ScrollToTop } from "./components/common/ScrollToTop";
import KeysPage from "./pages/KeysTables/Keys";
import GithubLogin from "./pages/Githublogin/Githublogin";


export default function App() {
  return (
    <>
      <Router>
        <ScrollToTop />
        <Routes>
          {/* Dashboard Layout */}
          <Route index path="/login" element={<GithubLogin />} />
          <Route element={<AppLayout />}>
            {/* <Route index path="/" element={<Home />} /> */}
            <Route index path="/" element={<ClusterList />} />
            <Route index path="/keys/:provider" element={<KeysPage />} />
            <Route index path="/keys/:provider" element={<KeysPage />} />
            <Route index path="/add-cluster" element={<AddCluster />} />
          </Route>
          {/* Fallback Route */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Router>
    </>
  );
}
