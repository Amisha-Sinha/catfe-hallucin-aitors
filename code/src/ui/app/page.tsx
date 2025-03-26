"use client"

import type React from "react"
import { useState, useRef, useEffect } from "react"
import { Avatar } from "@/components/ui/avatar"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Loader2, Send, Wrench } from "lucide-react"
import { v4 as uuidv4 } from "uuid"
import { initializeSocket, sendMessage as socketSendMessage, onReceiveMessage, onToolCall, onEndStream, onToolResult } from "@/lib/socket-service" // Import socket-service
import dynamic from "next/dynamic"

const ReactMarkdown = dynamic(() => import("react-markdown"), { ssr: false })

type Message = {
  id: string
  role: "user" | "assistant" 
  content: string
  createdAt?: Date
}

type ToolCall = {
  id: string
  status: boolean
  name: string
}

type ToolResponse = {
  tool_name: string
  tool_call_id: string
  content: string
}

type UnionClass = Message | ToolCall


export default function ChatInterface() {
  const [localMessages, setLocalMessages] = useState<UnionClass[]>([])
  const [inputValue, setInputValue] = useState("")
  const [isProcessing, setIsProcessing] = useState(false)
  const [currentTool, setCurrentTool] = useState<string | null>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Initialize socket connection
  useEffect(() => {
    const socket = initializeSocket()
    const unsubscribeMessage = onReceiveMessage((response: any) => {
      receiveMessage({
        id: uuidv4(),
        role: "assistant",
        content: response,
        createdAt: new Date(),
      })
    })

    const receiveToolCalls = onToolCall((toolCall: ToolCall) => {
      receiveMessage({
        id: toolCall.id,
        status: false,
        name: toolCall.name
      })
    })
  
    const onToolResponse = onToolResult((data: ToolResponse) => {
      setLocalMessages((prevMessages) =>
        prevMessages.map((msg) =>
          "id" in msg && msg.id === data.tool_call_id
            ? { ...msg, status: true }
            : msg
        )
      )
    })

    const onEnd = onEndStream(() => {
      setIsProcessing(false)
    })

    // Add welcome message
    setLocalMessages([
      {
        id: uuidv4(),
        role: "assistant",
        content: "Hello! I can help you get information about your project repositories. What would you like to know?",
        createdAt: new Date(),
      },
    ])

    return () => {
      unsubscribeMessage() 
      receiveToolCalls()
      onToolResponse()
      onEnd()// Clean up message listener
      socket.disconnect()
    }
  }, [])

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [localMessages])

  const sendMessage = (content: string) => {
    if (!content.trim()) return

    const message: Message = {
      id: uuidv4(),
      role: "user",
      content,
      createdAt: new Date(),
    }

    // Add to local messages
    setLocalMessages((prev) => [...prev, message])

    // Send via socket
    socketSendMessage(content)

    // Clear input and set processing state
    setInputValue("")
    setIsProcessing(true)
  }

  const receiveMessage = (unionClass: UnionClass) => {
    setLocalMessages((prev) => [...prev, unionClass])
  }


  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    sendMessage(inputValue)
  }


  return (
    <div className="flex flex-col h-screen mx-auto p-4" style={{ maxWidth: "80%", width: "100%" }}>
      <h1 className="text-2xl font-bold mb-4">Behave Yourself - Your BDD Buddy</h1>

      <Card className="flex-1 overflow-hidden flex flex-col mb-4 p-4">
        <div className="flex-1 overflow-y-auto pb-4">
          {localMessages.length === 0 ? (
            <div className="h-full flex items-center justify-center text-gray-400">Start a conversation</div>
          ) : (
            <div className="space-y-4">
              {localMessages.map((item) => (
                <div key={item.id} className="flex">
                  <div
                    className={`flex items-start max-w-1/2 break-words ${
                      "role" in item && item.role === "user" ? "ml-auto justify-end" : "mr-auto justify-start"
                    }`} // Ensure half-width and alignment
                    style={{ flex: "0 0 50%" }} // Explicitly set half-width
                  >
                    {"role" in item && item.role !== "user" && (
                      <Avatar className="h-8 w-8 mr-2">
                        <div className="bg-primary text-primary-foreground h-full w-full flex items-center justify-center text-xs">
                          AI
                        </div>
                      </Avatar>
                    )}
                    <div className="flex flex-col">
                      {"name" in item && (
                        <div className="text-xs text-gray-500 mb-1 flex items-center">
                          <Wrench className="h-3 w-3 mr-1" />
                          <span className="font-mono bg-gray-200 dark:bg-gray-700 px-1 rounded text-xs">
                            {item.name}
                          </span>
                          <span
                            className={`ml-2 text-xs font-semibold ${
                              item.status ? "text-green-500" : "text-red-500"
                            }`}
                          >
                            {item.status ? "Completed" : "Pending"}
                          </span>
                        </div>
                      )}
                      {"role" in item && (
                        <div
                          className={`p-3 rounded-lg whitespace-pre-wrap break-words ${
                            item.role === "user" ? "bg-primary text-primary-foreground" : "bg-muted"
                          }`}
                        >
                          <ReactMarkdown>{item.content}</ReactMarkdown>
                        </div>
                      )}
                      {"createdAt" in item && item.createdAt && (
                        <div className="text-xs text-gray-400 mt-1">
                          {item.createdAt.toLocaleString()}
                        </div>
                      )}
                    </div>
                    {"role" in item && item.role === "user" && (
                      <Avatar className="h-8 w-8 ml-2">
                        <div className="bg-secondary text-secondary-foreground h-full w-full flex items-center justify-center text-xs">
                          You
                        </div>
                      </Avatar>
                    )}
                  </div>
                </div>
              ))}
              {isProcessing && (
                <div className="flex justify-start">
                  <div className="flex items-start">
                    <Avatar className="h-8 w-8 mr-2">
                      <div className="bg-primary text-primary-foreground h-full w-full flex items-center justify-center text-xs">
                        AI
                      </div>
                    </Avatar>
                    <div className="flex flex-col">
                      {currentTool && (
                        <div className="text-xs text-gray-500 mb-1 flex items-center">
                          <Wrench className="h-3 w-3 mr-1" />
                          <span className="font-mono bg-gray-200 dark:bg-gray-700 px-1 rounded text-xs">
                            {currentTool}
                          </span>
                        </div>
                      )}
                      <div className="p-3 rounded-lg bg-muted">
                        <div className="flex space-x-1">
                          <div
                            className="h-2 w-2 bg-gray-400 rounded-full animate-bounce"
                            style={{ animationDelay: "0ms" }}
                          ></div>
                          <div
                            className="h-2 w-2 bg-gray-400 rounded-full animate-bounce"
                            style={{ animationDelay: "150ms" }}
                          ></div>
                          <div
                            className="h-2 w-2 bg-gray-400 rounded-full animate-bounce"
                            style={{ animationDelay: "300ms" }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>
      </Card>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <Input
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Type your message..."
          disabled={isProcessing}
          className="flex-1"
        />
        <Button type="submit" disabled={isProcessing || !inputValue.trim()}>
          {isProcessing ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
        </Button>
      </form>
    </div>
  )
}

