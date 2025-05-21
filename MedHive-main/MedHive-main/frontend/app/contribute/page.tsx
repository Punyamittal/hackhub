'use client';

import { useState } from 'react';
import Link from 'next/link';
import Image from 'next/image';

export default function ContributePage() {
  const [deviceSpecs, setDeviceSpecs] = useState({
    cpu: 'Checking...',
    memory: 'Checking...',
    gpu: 'Checking...',
    os: 'Checking...',
  });
  const [isParticipating, setIsParticipating] = useState(false);
  const [isContributor, setIsContributor] = useState(false);
  const [activeRounds, setActiveRounds] = useState([
    {
      id: 1,
      name: 'Pneumonia Detection',
      roundNumber: 3,
      estimatedTime: '15-20 minutes',
      dataSize: '~200MB',
      participants: 8,
      progress: 45,
    },
    {
      id: 2,
      name: 'ECG Analysis',
      roundNumber: 2,
      estimatedTime: '10-15 minutes',
      dataSize: '~150MB',
      participants: 6,
      progress: 30,
    },
  ]);
  const [selectedRound, setSelectedRound] = useState<number | null>(null);
  const [trainingProgress, setTrainingProgress] = useState(0);
  const [showConfirmation, setShowConfirmation] = useState(false);
  
  const startContributing = () => {
    setIsContributor(true);
  };
  
  const startTraining = (roundId: number) => {
    setSelectedRound(roundId);
    setIsParticipating(true);
    setTrainingProgress(0);
    
    // Simulate training progress
    const interval = setInterval(() => {
      setTrainingProgress(prevProgress => {
        if (prevProgress >= 100) {
          clearInterval(interval);
          setShowConfirmation(true);
          return 100;
        }
        return prevProgress + 5;
      });
    }, 1000);
  };
  
  const finishTraining = () => {
    setIsParticipating(false);
    setSelectedRound(null);
    setShowConfirmation(false);
    
    // Update the progress of the active round
    setActiveRounds(prevRounds => 
      prevRounds.map(round => 
        round.id === selectedRound 
          ? { ...round, progress: Math.min(round.progress + 15, 100) } 
          : round
      )
    );
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-3xl font-extrabold text-gray-900 dark:text-white sm:text-4xl">
            Contribute to Federated Learning
          </h1>
          <p className="mt-3 max-w-2xl mx-auto text-xl text-gray-500 dark:text-gray-400 sm:mt-4">
            Help improve healthcare AI models while preserving privacy and security.
          </p>
        </div>

        {!isContributor ? (
          <div className="max-w-3xl mx-auto bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-lg">
            <div className="px-4 py-5 sm:p-6">
              <div className="sm:flex sm:items-start sm:justify-between">
                <div>
                  <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">
                    Become a Contributor
                  </h3>
                  <div className="mt-2 max-w-xl text-sm text-gray-500 dark:text-gray-400">
                    <p>
                      Donate your excess computing resources to train and improve healthcare AI models.
                    </p>
                    <ul className="mt-4 list-disc pl-5 space-y-1">
                      <li>Your data never leaves your device</li>
                      <li>Models are trained securely on your machine</li>
                      <li>Contribute to advancing medical AI</li>
                      <li>Choose when and how long to contribute</li>
                    </ul>
                  </div>
                </div>
                <div className="mt-5 sm:mt-0 sm:ml-6 sm:flex-shrink-0">
                  <button
                    type="button"
                    onClick={startContributing}
                    className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:text-sm"
                  >
                    Get Started
                  </button>
                </div>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-12">
            {/* Device Information */}
            <div className="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-lg">
              <div className="px-4 py-5 sm:px-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">
                  Your Device Information
                </h3>
                <p className="mt-1 max-w-2xl text-sm text-gray-500 dark:text-gray-400">
                  Resources that will be used for federated learning.
                </p>
              </div>
              <div className="border-t border-gray-200 dark:border-gray-700 px-4 py-5 sm:p-0">
                <dl className="sm:divide-y sm:divide-gray-200 sm:dark:divide-gray-700">
                  <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">
                      CPU
                    </dt>
                    <dd className="mt-1 text-sm text-gray-900 dark:text-white sm:mt-0 sm:col-span-2">
                      {deviceSpecs.cpu}
                    </dd>
                  </div>
                  <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">
                      Memory
                    </dt>
                    <dd className="mt-1 text-sm text-gray-900 dark:text-white sm:mt-0 sm:col-span-2">
                      {deviceSpecs.memory}
                    </dd>
                  </div>
                  <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">
                      GPU
                    </dt>
                    <dd className="mt-1 text-sm text-gray-900 dark:text-white sm:mt-0 sm:col-span-2">
                      {deviceSpecs.gpu}
                    </dd>
                  </div>
                  <div className="py-4 sm:py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                    <dt className="text-sm font-medium text-gray-500 dark:text-gray-400">
                      Operating System
                    </dt>
                    <dd className="mt-1 text-sm text-gray-900 dark:text-white sm:mt-0 sm:col-span-2">
                      {deviceSpecs.os}
                    </dd>
                  </div>
                </dl>
              </div>
            </div>

            {/* Active Rounds */}
            {!isParticipating ? (
              <div className="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-lg">
                <div className="px-4 py-5 sm:px-6">
                  <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">
                    Active Federated Learning Rounds
                  </h3>
                  <p className="mt-1 max-w-2xl text-sm text-gray-500 dark:text-gray-400">
                    Select a model to contribute to training.
                  </p>
                </div>
                <div className="border-t border-gray-200 dark:border-gray-700">
                  <ul className="divide-y divide-gray-200 dark:divide-gray-700">
                    {activeRounds.map((round) => (
                      <li key={round.id} className="p-4 sm:px-6">
                        <div className="flex items-center justify-between">
                          <div className="flex-1 min-w-0">
                            <h4 className="text-lg font-medium text-gray-900 dark:text-white truncate">
                              {round.name}
                            </h4>
                            <p className="text-sm text-gray-500 dark:text-gray-400">
                              Round #{round.roundNumber} • {round.participants} participants • {round.estimatedTime} • {round.dataSize}
                            </p>
                            <div className="mt-2">
                              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                                <div className="bg-primary-600 h-2.5 rounded-full" style={{ width: `${round.progress}%` }}></div>
                              </div>
                              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                                Overall Progress: {round.progress}%
                              </p>
                            </div>
                          </div>
                          <div className="ml-4">
                            <button
                              onClick={() => startTraining(round.id)}
                              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                            >
                              Start Training
                            </button>
                          </div>
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ) : (
              <div className="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-lg">
                <div className="px-4 py-5 sm:px-6">
                  <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">
                    Training in Progress
                  </h3>
                  <p className="mt-1 max-w-2xl text-sm text-gray-500 dark:text-gray-400">
                    {activeRounds.find(r => r.id === selectedRound)?.name} - Round #{activeRounds.find(r => r.id === selectedRound)?.roundNumber}
                  </p>
                </div>
                <div className="border-t border-gray-200 dark:border-gray-700 px-4 py-5 sm:p-6">
                  <div className="mb-6">
                    <div className="w-full h-6 bg-gray-200 dark:bg-gray-700 rounded-full">
                      <div 
                        className="h-6 bg-primary-600 rounded-full flex items-center justify-center text-xs font-medium text-white" 
                        style={{ width: `${trainingProgress}%` }}
                      >
                        {trainingProgress}%
                      </div>
                    </div>
                  </div>
                  
                  <div className="text-center">
                    <p className="mb-4 text-sm text-gray-500 dark:text-gray-400">
                      Please keep this window open. You can minimize it, but don't close it until training is complete.
                    </p>
                    <button
                      disabled
                      className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-gray-400 cursor-not-allowed"
                    >
                      Training in Progress
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
        
        {/* Confirmation Modal */}
        {showConfirmation && (
          <div className="fixed z-10 inset-0 overflow-y-auto">
            <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
              <div className="fixed inset-0 transition-opacity" aria-hidden="true">
                <div className="absolute inset-0 bg-gray-500 opacity-75"></div>
              </div>
              <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
              <div className="inline-block align-bottom bg-white dark:bg-gray-800 rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
                <div className="bg-white dark:bg-gray-800 px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                  <div className="sm:flex sm:items-start">
                    <div className="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-green-100 sm:mx-0 sm:h-10 sm:w-10">
                      <svg className="h-6 w-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    <div className="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                      <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">
                        Training Complete!
                      </h3>
                      <div className="mt-2">
                        <p className="text-sm text-gray-500 dark:text-gray-400">
                          Thank you for contributing to improve healthcare AI models. Your contribution has been successfully processed and added to the federated learning round.
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="bg-gray-50 dark:bg-gray-700 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                  <button 
                    type="button" 
                    onClick={finishTraining}
                    className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-primary-600 text-base font-medium text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 sm:ml-3 sm:w-auto sm:text-sm"
                  >
                    Continue
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
} 