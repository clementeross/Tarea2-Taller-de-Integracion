import React, { useState } from "react";
import Chat from "./componentes/Chat";
import "./App.css";
import Map from './componentes/Map';

function App() {
  const [name, setName] = useState("");
  const [registered, setRegistered] = useState(false);

  const register = (e) => {
    e.preventDefault();
    if (name !== "") {
      setRegistered(true);
    }
  };

  return (
    <div className="container">
      <h1>Bienvenid@ a la Tarea 3 de Clemente Ross</h1>
      <div className="wrapper">
        <Map/>
        {!registered && (
          <form className="chatContainer" onSubmit={register}>
            <label>Escriba su nombre</label>
            <input className="inputName" value={name} onChange={(e) => setName(e.target.value)} />
            <button>Ir al chat</button>
          </form>
        )}

        {registered && (
          <Chat name={name} />
        )}
      </div>
    </div>
  );
}

export default App;
