// In frontend/app/page.tsx

'use client'; // This is a Next.js directive that marks this as a Client Component.

import { useState } from 'react';

export default function Home() {
  // --- STATE MANAGEMENT ---
  // We use React's useState hook to manage the state of our application.
  const [file, setFile] = useState<File | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [question, setQuestion] = useState<string>('');
  const [persona, setPersona] = useState<string>('formal'); // Default persona
  const [answer, setAnswer] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');
  const [fileName, setFileName] = useState<string>('');

  // --- HANDLER FUNCTIONS ---

  // Handles the file input change
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files) {
      setFile(event.target.files[0]);
    }
  };

  // Handles the PDF upload process
  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first.');
      return;
    }

    // Reset state for a new upload
    setIsLoading(true);
    setError('');
    setAnswer('');
    setSessionId(null);
    setFileName('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      // API call to our Python backend's /upload endpoint
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Failed to upload file.');
      }

      const data = await response.json();
      setSessionId(data.session_id);
      setFileName(data.filename);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Handles the question submission
  const handleAskQuestion = async () => {
    if (!sessionId || !question) {
      setError('Please upload a document and ask a question.');
      return;
    }

    setIsLoading(true);
    setError('');
    setAnswer('');

    try {
      // API call to our Python backend's /ask endpoint
      const response = await fetch('http://localhost:8000/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, question, persona }),
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Failed to get an answer.');
      }

      const data = await response.json();
      setAnswer(data.answer);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // --- JSX FOR THE UI ---
  // This is the HTML-like structure of our app, styled with Tailwind CSS classes.
  return (
    <main className="flex min-h-screen flex-col items-center p-12 bg-gray-50 font-sans">
      <div className="w-full max-w-3xl">
        <h1 className="text-4xl font-bold text-center text-gray-800 mb-8">
          Offline PDF Q&A Assistant
        </h1>
        
        {/* Step 1: File Upload Section */}
        <div className="p-6 bg-white border rounded-lg shadow-md mb-6">
          <h2 className="text-2xl font-semibold text-gray-700 mb-4">1. Upload Your PDF</h2>
          <div className="flex items-center space-x-4">
            <input 
              type="file" 
              accept=".pdf" 
              onChange={handleFileChange}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
            <button 
              onClick={handleUpload} 
              disabled={!file || (isLoading && !sessionId)}
              className="px-5 py-2 bg-blue-600 text-white font-semibold rounded-lg shadow-md disabled:bg-gray-400 hover:bg-blue-700 transition duration-300"
            >
              {isLoading && !sessionId ? 'Processing...' : 'Process PDF'}
            </button>
          </div>
          {sessionId && <p className="text-green-600 mt-3 font-medium">✔ Successfully processed: <strong>{fileName}</strong></p>}
        </div>

        {/* Step 2: Ask a Question Section (only shows after a PDF is processed) */}
        {sessionId && (
          <div className="p-6 bg-white border rounded-lg shadow-md transition-opacity duration-500 animate-fadeIn">
            <h2 className="text-2xl font-semibold text-gray-700 mb-4">2. Ask a Question</h2>
            <div className="space-y-4">
              <textarea 
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                placeholder="e.g., What is the main conclusion of the document?"
                className="w-full p-3 border rounded-md h-24 focus:ring-2 focus:ring-blue-500 transition"
              />
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <label htmlFor="persona-select" className="font-semibold text-gray-600">Response Persona:</label>
                  <select 
                    id="persona-select"
                    value={persona}
                    onChange={(e) => setPersona(e.target.value)}
                    className="p-2 border rounded-md focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="formal">Formal</option>
                    <option value="friendly">Friendly</option>
                    <option value="skeptical">Skeptical</option>
                  </select>
                </div>
                <button 
                  onClick={handleAskQuestion} 
                  disabled={isLoading}
                  className="px-5 py-2 bg-green-600 text-white font-semibold rounded-lg shadow-md disabled:bg-gray-400 hover:bg-green-700 transition duration-300"
                >
                  {isLoading ? 'Thinking...' : 'Get Answer'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Display Area for Errors or the Final Answer */}
        <div className="mt-6">
          {error && <p className="text-red-600 bg-red-100 p-4 rounded-md font-medium">{error}</p>}
          {answer && !isLoading && (
            <div className="p-6 bg-gray-100 border rounded-lg animate-fadeIn">
              <h3 className="text-xl font-semibold text-gray-800 mb-2">Answer:</h3>
              <p className="text-gray-700 whitespace-pre-wrap leading-relaxed">{answer}</p>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}