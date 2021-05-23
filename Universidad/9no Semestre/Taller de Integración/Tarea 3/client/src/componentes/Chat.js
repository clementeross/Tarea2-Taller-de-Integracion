import React, { useState, useEffect, useRef } from "react";
import "../App.css";
import { io } from 'socket.io-client';

let socket = io("wss://tarea-3-websocket.2021-1.tallerdeintegracion.cl", {path: '/flights'});

const Chat = ({ name }) => {

  const getDate = (...args) => {
    var today = new Date();
    if (args.length > 0) {
      today = new Date(args[0]);
    }
    var dd = String(today.getDate()).padStart(2, '0');
    var mm = String(today.getMonth() + 1).padStart(2, '0'); //January is 0!
    var yyyy = today.getFullYear();
    var hh = String(today.getHours()).padStart(2, '0');
    var min = String(today.getMinutes()).padStart(2, '0');
    var ss = String(today.getSeconds()).padStart(2, '0');

    today = dd + '/' + mm + '/' + yyyy + ' - ' + hh + ':' + min + ':' + ss;
    return today;
  }

  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    socket.on("CHAT", (obj) => {
      setMessages([...messages, obj]);
    });

    return () => {
      socket.off();
    };
  }, [messages]);

  const divRef = useRef(null);
  useEffect(() => {
    divRef.current.scrollIntoView({ behavior: "smooth" });
  });

  const submit = (e) => {
    e.preventDefault();
    const obj = {
      "name": name, 
      "message": message, 
      "date": getDate()
    }
    socket.emit("CHAT", obj);
    setMessage("");
  };

  return (
    <div className="chatContainer">
      <div className="chat">
        {messages.map((e, i) => (
          <div key={i}>
            <div>{getDate(e.date)}</div>
            <div><b>{e.name}:</b> {e.message}</div>
          </div>
        ))}
        <div ref={divRef}></div>
      </div>
      <form onSubmit={submit}>
        <br></br>
        <textarea
          className="message"
          value={message}
          placeholder="Escriba su mensaje..."
          onChange={(e) => {
            setMessage(e.target.value)
          }}
        ></textarea>
        <br></br>
        <button>Enviar</button>
      </form>
    </div>
  );
};

export default Chat;