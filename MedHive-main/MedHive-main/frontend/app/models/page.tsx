'use client';

import * as React from 'react';
import Link from 'next/link';

interface Model {
  id: number;
  name: string;
  description: string;
  category: string;
  accuracy: number;
  created: string;
  version: string;
  contributors: number;
  downloadCount: number;
  imageUrl: string;
}

export default function ModelsPage() {
  const [models, setModels] = React.useState<Model[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);
  const [activeCategory, setActiveCategory] = React.useState('All');
  const [searchQuery, setSearchQuery] = React.useState('');
  
  const categories = ['All', 'Radiology', 'Cardiology', 'Pathology', 'Neurology', 'General'];

  React.useEffect(() => {
    // Simulate fetching models data
    const mockModels: Model[] = [
      {
        id: 1,
        name: "Pneumonia Detection",
        description: "Detects pneumonia from chest X-rays with high precision.",
        category: "Radiology",
        accuracy: 92.5,
        created: "2023-05-15",
        version: "v2.3",
        contributors: 127,
        downloadCount: 1245,
        imageUrl: "/images/models/pneumonia.jpg"
      },
      {
        id: 2,
        name: "ECG Analyzer",
        description: "Identifies cardiac abnormalities from ECG recordings.",
        category: "Cardiology",
        accuracy: 94.1,
        created: "2023-06-22",
        version: "v1.8",
        contributors: 84,
        downloadCount: 876,
        imageUrl: "/images/models/ecg.jpg"
      },
      {
        id: 3,
        name: "Skin Lesion Classifier",
        description: "Classifies skin lesions and identifies potential melanomas.",
        category: "Pathology",
        accuracy: 89.7,
        created: "2023-04-03",
        version: "v2.1",
        contributors: 103,
        downloadCount: 912,
        imageUrl: "/images/models/skin.jpg"
      },
      {
        id: 4,
        name: "Brain Tumor Segmentation",
        description: "Segments brain MRI images to identify and localize tumors.",
        category: "Neurology",
        accuracy: 91.3,
        created: "2023-07-10",
        version: "v1.5",
        contributors: 76,
        downloadCount: 654,
        imageUrl: "/images/models/brain.jpg"
      },
      {
        id: 5,
        name: "Medical Text Analyzer",
        description: "Extracts medical information from clinical notes.",
        category: "General",
        accuracy: 87.9,
        created: "2023-03-29",
        version: "v3.0",
        contributors: 95,
        downloadCount: 1089,
        imageUrl: "/images/models/text.jpg"
      }
    ];
    
    setTimeout(() => {
      setModels(mockModels);
      setIsLoading(false);
    }, 1000);
  }, []);

  const filteredModels = models.filter((model: Model) => {
    const matchesCategory = activeCategory === 'All' || model.category === activeCategory;
    const matchesSearch = model.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
                         model.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const formatDate = (dateString: string) => {
    const options: Intl.DateTimeFormatOptions = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-3xl font-extrabold text-gray-900 dark:text-white sm:text-4xl">
            Healthcare AI Models
          </h1>
          <p className="mt-3 max-w-2xl mx-auto text-xl text-gray-500 dark:text-gray-400 sm:mt-4">
            Explore our library of federated learning models for healthcare applications.
          </p>
        </div>

        {/* Search and Filter */}
        <div className="mb-8 flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
          <div className="w-full md:w-auto">
            <div className="flex space-x-2 overflow-x-auto pb-2">
              {categories.map((category) => (
                <button
                  key={category}
                  onClick={() => setActiveCategory(category)}
                  className={`px-4 py-2 text-sm font-medium rounded-md whitespace-nowrap ${
                    activeCategory === category
                      ? 'bg-primary-600 text-white'
                      : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  {category}
                </button>
              ))}
            </div>
          </div>
          
          <div className="w-full md:w-64">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <input
                type="text"
                placeholder="Search models..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-700 rounded-md leading-5 bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              />
            </div>
          </div>
        </div>

        {/* Models Grid */}
        {isLoading ? (
          <div className="flex justify-center items-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {filteredModels.map((model) => (
              <div key={model.id} className="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg">
                <div className="h-48 w-full bg-gray-200 dark:bg-gray-700">
                  {/* Image placeholder */}
                  <div className="h-full w-full flex items-center justify-center bg-gray-300 dark:bg-gray-600">
                    <svg className="h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                    </svg>
                  </div>
                </div>
                <div className="px-4 py-5 sm:p-6">
                  <div className="flex items-center justify-between">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 dark:bg-primary-900 text-primary-800 dark:text-primary-300">
                      {model.category}
                    </span>
                    <span className="inline-flex items-center text-sm text-gray-500 dark:text-gray-400">
                      {model.version}
                    </span>
                  </div>
                  <h3 className="mt-4 text-lg font-medium text-gray-900 dark:text-white">
                    {model.name}
                  </h3>
                  <div className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                    <p>{model.description}</p>
                  </div>
                  <div className="mt-4">
                    <div className="flex items-center">
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Accuracy</span>
                      <span className="ml-auto text-sm font-medium text-gray-900 dark:text-white">{model.accuracy}%</span>
                    </div>
                    <div className="mt-1 w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div 
                        className="bg-primary-600 h-2 rounded-full" 
                        style={{ width: `${model.accuracy}%` }}
                      />
                    </div>
                  </div>
                  <div className="mt-5 flex items-center text-sm text-gray-500 dark:text-gray-400 space-x-4">
                    <div className="flex items-center">
                      <svg className="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                      </svg>
                      {model.contributors} contributors
                    </div>
                    <div className="flex items-center">
                      <svg className="flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                      </svg>
                      {model.downloadCount} downloads
                    </div>
                  </div>
                  <div className="mt-6">
                    <Link href={`/models/${model.id}`} className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 w-full justify-center">
                      View Details
                    </Link>
                  </div>
                </div>
                <div className="bg-gray-50 dark:bg-gray-700 px-4 py-4 sm:px-6">
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    Created on {formatDate(model.created)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
        
        {/* No Results */}
        {!isLoading && filteredModels.length === 0 && (
          <div className="text-center py-20">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No models found</h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Try adjusting your search or filter to find what you're looking for.
            </p>
            <div className="mt-6">
              <button
                onClick={() => {
                  setActiveCategory('All');
                  setSearchQuery('');
                }}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                Clear Filters
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 