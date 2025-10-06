# 🌍 Travel Planner App

[![Demo – Chat with AI Assistant](media/konwa.gif)](media/konwa.gif)
[![Demo – Travel Plan Generation](media/output.gif)](media/output.gif)

**Travel Planner App** is an intelligent web application powered by **LLM (Large Language Model)** technology that helps users plan their trips in an interactive and automated way.  

---

## ✈️ Description

The application allows users to:
- create multiple **trips**,  
- chat with an AI assistant in the context of each trip,  
- automatically **update travel information**,  
- integrate with **Google Maps API** and **Kiwi.com API** to enrich the plan with locations, hotels, and flights.  

Each trip is stored as a structured JSON object that is dynamically updated by the LLM model based on the user’s conversation with the assistant.

---

## 🧠 How It Works

1. The user logs into the application (JWT authentication + MongoDB).  
2. A new trip is created in the sidebar (`New Trip`).  
3. The user chats with the AI assistant, which analyzes the context and generates a detailed travel plan.  
4. The plan is automatically enriched with data from **Google Maps API** — including coordinates, addresses, and map links.  
5. The user can:
   - edit the plan,  
   - browse checklists,  
   - export the plan to PDF.  

---

## ⚙️ Technologies

- **Frontend:** Next.js + React + Tailwind CSS + shadcn/ui  
- **Backend:** FastAPI + LangChain + Together.ai  
- **Database:** MongoDB Atlas  
- **Integrations:** Google Maps API, Google Places API, Kiwi.com API (via RapidAPI)  

---

## 📄 Author

Project developed as an **engineering thesis** in Computer Science.  
Author: *Mikołaj Taudul*  
Year: 2025  

---
