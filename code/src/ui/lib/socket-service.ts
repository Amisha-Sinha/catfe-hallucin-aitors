import { io, type Socket } from "socket.io-client"

let socket: Socket | null = null

export const initializeSocket = () => {
  if (!socket) {
    socket = io("http://localhost:12345/socket/chat", { // Connect to /socket/chat namespace
      path: "/socket.io", // Default Socket.IO path
      transports: ["websocket"], // Use WebSocket transport to avoid polling
    })

    socket.on("connect", () => {
      console.log("Socket connected with ID:", socket?.id)
    })

    socket.on("disconnect", () => {
      console.log("Socket disconnected")
    })

    socket.on("connect_error", (error) => {
      console.error("Socket connection error:", error)
    })
  }

  return socket
}

export const getSocket = () => {
  if (!socket) {
    return initializeSocket()
  }
  return socket
}

export const disconnectSocket = () => {
  if (socket) {
    socket.disconnect()
    socket = null
  }
}

export const sendMessage = (message: any) => {
  const socketInstance = getSocket()
  if (socketInstance) {
    socketInstance.emit("message", message) // Emit message to /socket/chat
  }
}

export const onReceiveMessage = (callback: (message: any) => void) => {
  const socketInstance = getSocket()
  if (socketInstance) {
    socketInstance.on("response", callback) // Listen for responses from /socket/chat
  }

  return () => {
    if (socketInstance) {
      socketInstance.off("response", callback)
    }
  }
}

export const onToolResult = (callback: (data: any) => void) => {
  const socketInstance = getSocket()
  if (socketInstance) {
    socketInstance.on("tool_response", callback)
  }

  return () => {
    if (socketInstance) {
      socketInstance.off("tool_response", callback)
    }
  }
}


export const onToolCall = (callback: (data: any) => void) => {
  const socketInstance = getSocket()
  if (socketInstance) {
    socketInstance.on("tool_call", callback)
  }

  return () => {
    if (socketInstance) {
      socketInstance.off("tool_call", callback)
    }
  }
}



export const onEndStream = (callback: (data: any) => void) => {
  const socketInstance = getSocket()
  if (socketInstance) {
    socketInstance.on("end", callback)
  }

  return () => {
    if (socketInstance) {
      socketInstance.off("end", callback)
    }
  }
}


