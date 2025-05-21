import Link from 'next/link';
import Image from 'next/image';
import dynamic from 'next/dynamic';

// Load the Chatbot component dynamically with client-side rendering
const Chatbot = dynamic(() => import('../components/Chatbot'), { ssr: false });

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center">
      <nav className="w-full bg-white shadow-md dark:bg-gray-900">
        <div className="container mx-auto px-6 py-3 flex justify-between items-center">
          <div className="flex items-center">
            <span className="text-2xl font-bold text-primary-600">HackathonHub</span>
          </div>
          <div className="space-x-4">
            <Link href="/admin" className="text-gray-700 hover:text-primary-600 dark:text-gray-300">Admin Portal</Link>
            <Link href="/models" className="text-gray-700 hover:text-primary-600 dark:text-gray-300">Model Hive</Link>
            <Link href="/contribute" className="text-gray-700 hover:text-primary-600 dark:text-gray-300">Contribute</Link>
            <button className="btn-primary">Sign In</button>
          </div>
        </div>
      </nav>

      <section className="container mx-auto px-6 py-12">
        <div className="flex flex-col md:flex-row items-center">
          <div className="md:w-1/2 mb-8 md:mb-0">
            <h1 className="text-4xl font-bold mb-4 text-gray-800 dark:text-white">
              AI-Powered Healthcare with Privacy-Preserving Federated Learning
            </h1>
            <p className="text-lg text-gray-600 dark:text-gray-300 mb-6">
              HackathonHub uses Groq&apos;s ultra-fast inference to deliver real-time health insights while protecting patient data through secure federated learning.
            </p>
            <div className="flex space-x-4">
              <button className="btn-primary">Get Started</button>
              <button className="btn-secondary">Learn More</button>
            </div>
          </div>
          <div className="md:w-1/2 flex justify-center">
            <div className="w-full max-w-md h-64 bg-gray-200 rounded-lg relative">
              {/* Placeholder for hero image */}
              <div className="absolute inset-0 flex items-center justify-center text-gray-500">
                Medical AI Image Placeholder
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="w-full bg-gray-100 dark:bg-gray-800 py-12">
        <div className="container mx-auto px-6">
          <h2 className="text-3xl font-bold text-center mb-8 text-gray-800 dark:text-white">
            Our AI Powered Models
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              { title: "LLM Symptom Analysis", description: "AI-powered health assessment using Groq inference" },
              { title: "ECG Curve Analysis", description: "Analyze ECG patterns with GraphRAG technology" },
              { title: "Pneumonia Detection", description: "X-ray image analysis for pneumonia detection" },
              { title: "Breast Cancer Detection", description: "Early detection using advanced imaging analysis" },
              { title: "Glaucoma Detection", description: "FUNDUS image analysis for glaucoma screening" }
            ].map((model, index) => (
              <div key={index} className="card hover:shadow-lg transition-shadow">
                <h3 className="text-xl font-semibold mb-2 text-gray-800 dark:text-white">{model.title}</h3>
                <p className="text-gray-600 dark:text-gray-300 mb-4">{model.description}</p>
                <Link href={`/models/${index + 1}`} className="text-primary-600 hover:text-primary-700 font-medium">
                  Explore Model &rarr;
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="container mx-auto px-6 py-12">
        <h2 className="text-3xl font-bold text-center mb-8 text-gray-800 dark:text-white">
          How It Works
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center">
            <div className="bg-primary-100 dark:bg-primary-900 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-primary-600 dark:text-primary-300 text-2xl font-bold">1</span>
            </div>
            <h3 className="text-xl font-semibold mb-2 text-gray-800 dark:text-white">Privacy-First Data</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Hospitals and research centers keep sensitive data local, training models without sharing raw data.
            </p>
          </div>
          <div className="text-center">
            <div className="bg-primary-100 dark:bg-primary-900 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-primary-600 dark:text-primary-300 text-2xl font-bold">2</span>
            </div>
            <h3 className="text-xl font-semibold mb-2 text-gray-800 dark:text-white">Federated Learning</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Local model updates are securely aggregated to build a robust global model without exposing patient information.
            </p>
          </div>
          <div className="text-center">
            <div className="bg-primary-100 dark:bg-primary-900 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-primary-600 dark:text-primary-300 text-2xl font-bold">3</span>
            </div>
            <h3 className="text-xl font-semibold mb-2 text-gray-800 dark:text-white">Ultra-Fast Inference</h3>
            <p className="text-gray-600 dark:text-gray-300">
              Groq-powered AI delivers real-time health insights and recommendations with exceptional performance.
            </p>
          </div>
        </div>
      </section>

      {/* Chatbot component */}
      <Chatbot />
    </main>
  );
} 