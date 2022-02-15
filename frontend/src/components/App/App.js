import React from "react";
import { BrowserRouter, Routes, Route} from "react-router-dom";
import { 
  LandingPage, 
  Layout,
  LoginPage,
  ProfilePage,
  RegistrationPage,
  NotfoundPage
} from "../../components/"

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/registration" element={<RegistrationPage />} />
          <Route path="*" element={<NotfoundPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}