'use client';

import { useState } from 'react';

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [isCopied, setIsCopied] = useState(false);
  const [showReadable, setShowReadable] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setError('Please select a file first.');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

    try {
      const response = await fetch(`${apiUrl}/parse`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || 'Failed to parse file.');
      }

      const data = await response.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred.');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    if (result) {
      navigator.clipboard.writeText(JSON.stringify(result, null, 2));
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans p-4 sm:p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        
        {/* Header Section */}
        <header className="flex flex-col items-center justify-center pb-6 border-b border-gray-200 text-center">
          <h1 className="text-3xl font-bold text-gray-900 tracking-tight">Excel Data Parser</h1>
          <p className="mt-1 text-sm text-gray-500">Autonomous extraction of factory operational data into a strict taxonomy.</p>
        </header>

        {/* Upload Form */}
        <section className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row items-end gap-4">
            <div className="flex-grow w-full">
              <label htmlFor="file-upload" className="block text-sm font-medium text-gray-700 mb-2">
                Upload Target Spreadsheet
              </label>
              <div className="flex items-center w-full">
                <input
                  id="file-upload"
                  type="file"
                  accept=".xlsx, .xls"
                  onChange={handleFileChange}
                  className="block w-full text-sm text-gray-600 file:mr-4 file:py-2.5 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer border border-gray-300 rounded-md shadow-sm bg-white"
                />
              </div>
            </div>
            <button
              type="submit"
              disabled={loading || !file}
              className="w-full sm:w-auto flex-none flex justify-center py-2.5 px-6 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                   <svg className="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                     <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                     <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                   </svg>
                   Parsing AI...
                </span>
              ) : 'Extract Data'}
            </button>
          </form>

          {error && (
            <div className="mt-4 bg-red-50 border-l-4 border-red-500 p-4 rounded-md">
              <p className="text-sm text-red-700 font-medium whitespace-pre-wrap">{error}</p>
            </div>
          )}
        </section>

        {/* Dashboard and JSON Views */}
        {result && (
          <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            
            {/* Metric Cards */}
            <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-white rounded-xl shadow-sm border border-green-100 p-5 border-l-4 border-l-green-500">
                <div className="text-sm font-medium text-green-600 uppercase tracking-wider mb-1">Data Points Mapped</div>
                <div className="text-3xl font-bold text-gray-900">{result.parsed_data?.length || 0}</div>
                <p className="mt-1 text-xs text-gray-500">High & Medium Confidence</p>
              </div>
              
              <div className="bg-white rounded-xl shadow-sm border border-yellow-100 p-5 border-l-4 border-l-yellow-400">
                <div className="text-sm font-medium text-yellow-600 uppercase tracking-wider mb-1">Needs Human Review</div>
                <div className="text-3xl font-bold text-gray-900">{result.needs_review?.length || 0}</div>
                <p className="mt-1 text-xs text-gray-500">Low Confidence Guesses</p>
              </div>

              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-5 border-l-4 border-l-gray-400">
                <div className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-1">Unmapped Columns</div>
                <div className="text-3xl font-bold text-gray-900">{result.unmapped_columns?.length || 0}</div>
                <p className="mt-1 text-xs text-gray-500">Comments & Metadata</p>
              </div>

              <div className="bg-white rounded-xl shadow-sm border border-red-100 p-5 border-l-4 border-l-red-500">
                <div className="text-sm font-medium text-red-600 uppercase tracking-wider mb-1">Warnings</div>
                <div className="text-3xl font-bold text-gray-900">{result.warnings?.length || 0}</div>
                <p className="mt-1 text-xs text-gray-500">Validation Flags</p>
              </div>
            </section>

            {/* Developer Payload View */}
            <section className="bg-[#0A0A0A] rounded-xl shadow-xl border border-gray-800 overflow-hidden flex flex-col">
              <div className="flex items-center justify-between px-4 py-3 bg-[#111111] border-b border-gray-800">
                <div className="flex items-center gap-3">
                  <div className="flex gap-1.5">
                    <div className="w-3 h-3 rounded-full bg-red-500"></div>
                    <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
                    <div className="w-3 h-3 rounded-full bg-green-500"></div>
                  </div>
                  <h3 className="text-sm font-medium text-gray-300 font-mono tracking-tight">API Response Payload</h3>
                </div>
                <button
                  onClick={handleCopy}
                  className={`text-xs px-3 py-1.5 rounded transition-colors border ${
                    isCopied 
                      ? 'bg-green-500/10 text-green-400 border-green-500/20' 
                      : 'bg-gray-800 text-gray-400 border-gray-700 hover:bg-gray-700 hover:text-gray-300'
                  }`}
                >
                  {isCopied ? 'Copied!' : 'Copy'}
                </button>
              </div>
              <div className="p-4 overflow-auto max-h-[400px] custom-scrollbar">
                <pre className="text-sm font-mono text-[#D4D4D4] whitespace-pre">
                  {JSON.stringify(result, null, 2)}
                </pre>
              </div>
            </section>

            {/* User Readable View Toggle */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <button 
                onClick={() => setShowReadable(!showReadable)}
                className="w-full px-6 py-4 flex items-center justify-between bg-gray-50 hover:bg-gray-100 transition-colors border-b border-gray-200"
              >
                <div className="flex items-center gap-3">
                  <svg className={`w-5 h-5 text-gray-500 transition-transform ${showReadable ? 'rotate-90' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
                  </svg>
                  <h3 className="text-lg font-semibold text-gray-800">Human Readable Data View</h3>
                </div>
                <span className="text-sm text-blue-600 font-medium">{showReadable ? 'Hide Table' : 'Show Table'}</span>
              </button>

              {showReadable && (
                <div className="p-0 overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Sheet</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Asset</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Parameter</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Raw Input</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Parsed Target</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Confidence</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {result.parsed_data?.map((point: any, idx: number) => (
                        <tr key={idx} className="hover:bg-gray-50">
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 border-r border-gray-100">{point.sheet_name || '-'}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 border-r border-gray-100">{point.asset_name || 'Generic'}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-blue-600 border-r border-gray-100 font-mono">{point.param_name}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 bg-red-50/30 border-r border-red-100 italic">"{point.raw_value}"</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-green-700 font-bold bg-green-50/30 border-r border-green-100">{point.parsed_value}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                              point.confidence === 'high' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                            }`}>
                              {point.confidence}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {(!result.parsed_data || result.parsed_data.length === 0) && (
                     <div className="p-8 text-center text-gray-500">No data points were successfully mapped.</div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      <style dangerouslySetInnerHTML={{__html: `
        .custom-scrollbar::-webkit-scrollbar {
          width: 10px;
          height: 10px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: #0A0A0A; 
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: #333333; 
          border-radius: 5px;
          border: 2px solid #0A0A0A;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: #555555; 
        }
      `}} />
    </div>
  );
}
