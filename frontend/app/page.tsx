"use client";

import { useState } from "react";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError("Please select a file first.");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://127.0.0.1:8000/parse", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Failed to parse file.");
      }

      const data = await response.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center py-12 px-4 sm:px-6 lg:px-8 font-sans text-gray-900">
      <div className="max-w-4xl w-full space-y-8">
        <div className="text-center">
          <h1 className="text-4xl font-extrabold text-gray-900 tracking-tight sm:text-5xl">
            Intelligent Excel Parser
          </h1>
          <p className="mt-4 text-xl text-gray-500">
            Upload factory operations data (.xlsx) to magically map, extract,
            and convert them to structured JSON.
          </p>
        </div>

        <div className="bg-white px-8 py-8 shadow-sm rounded-xl border border-gray-200">
          <form className="space-y-6" onSubmit={handleSubmit}>
            <div>
              <label
                htmlFor="file-upload"
                className="block text-sm font-medium text-gray-700"
              >
                Upload Data File
              </label>
              <div className="mt-2 text-left">
                <input
                  id="file-upload"
                  type="file"
                  accept=".xlsx, .xls"
                  onChange={handleFileChange}
                  className="block w-full text-sm text-gray-500 file:mr-4 file:py-2.5 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer border border-gray-300 rounded-md shadow-sm"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading || !file}
              className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? "Parsing AI..." : "Parse and Extract Data"}
            </button>
          </form>

          {error && (
            <div className="mt-6 bg-red-50 border-l-4 border-red-400 p-4 rounded-md">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <svg
                    className="h-5 w-5 text-red-400"
                    xmlns="http://www.w3.org/2000/svg"
                    viewBox="0 0 20 20"
                    fill="currentColor"
                    aria-hidden="true"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                      clipRule="evenodd"
                    />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-red-700 font-medium whitespace-pre-wrap">
                    {error}
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {result && (
          <div className="bg-gray-900 shadow-2xl rounded-xl overflow-hidden mt-8 border border-gray-800">
            <div className="px-6 py-4 border-b border-gray-800 bg-gray-900 flex justify-between items-center">
              <h3 className="text-lg leading-6 font-medium text-gray-100 flex items-center">
                <span className="h-3 w-3 bg-green-500 rounded-full mr-3 animate-pulse"></span>
                Parse Result
              </h3>
              <div className="text-xs text-gray-400 font-mono bg-gray-800 px-3 py-1 rounded">
                Status: {result.status || "success"}
              </div>
            </div>
            <div className="p-0">
              <pre className="text-sm text-green-400 font-mono overflow-auto p-6 max-h-[600px] bg-[#0d1117] custom-scrollbar">
                {JSON.stringify(result, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>

      <style
        dangerouslySetInnerHTML={{
          __html: `
        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
          height: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: #0d1117; 
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #30363d; 
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #484f58; 
        }
      `,
        }}
      />
    </div>
  );
}
