// services/Toast-Container.js
import React from 'react';
import { ToastContainer, Bounce } from 'react-toastify';

const ToastSetup = () => (
  <ToastContainer
  position="top-center"
  autoClose={2500}
  newestOnTop={false}
  closeOnClick={false}
  rtl={false}
  pauseOnFocusLoss
  draggable
  pauseOnHover
  theme="light"
  transition={Bounce}
  />
);

export default ToastSetup;
