# Github-
# 🎵 RepoRhythm

> Transform your GitHub commit history into music!

![RepoRhythm Demo](demo.gif)

## ✨ Features

- 🎹 **8 Music Styles**: Electronic, Classical, Rock, Jazz, Ambient, Chiptune, Lo-fi, Orchestral
- 🎼 **Smart Mapping**: Commit types → instruments, changes → dynamics
- 🥁 **Full Arrangement**: Melody, chords, bass, and drums
- 📥 **MIDI Export**: Download and import to your DAW
- 🎨 **Beautiful Visualizer**: See your music come alive

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- GitHub Token (optional, increases rate limit)

### Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your GitHub token
uvicorn app.main:app --reload