"use client";

import React, { useState, useEffect } from 'react';
import { ConnectButton } from '@rainbow-me/rainbowkit';
import type { NextPage } from 'next';
import Head from 'next/head';
import styles from '../styles/Home.module.css';
import { bridgeAbi } from '../abis/bridge';;
import { erc20Abi, defineChain, Address } from 'viem';
import { useAccount, useReadContract, useWriteContract } from 'wagmi';
import { sepolia } from 'wagmi/chains';
import { http, createConfig } from '@wagmi/core';
import { InformationCircleIcon, CurrencyDollarIcon, LightningBoltIcon } from '@heroicons/react/outline';

// wagmi doesnt have shibuya defined
export const shibuya = defineChain({
  id: 81,
  name: 'AstarShibuya',
  network: 'astar-shibuya',
  nativeCurrency: {
    name: 'SBY',
    symbol: 'SBY',
    decimals: 18,
  },
  rpcUrls: {
    default: { http: ['https://evm.shibuya.astar.network/'] },
  },
  testnet: true,
  contracts: {}
});

const config = createConfig({
  chains: [sepolia, shibuya],
  transports: {
    [sepolia.id]: http(),
    [shibuya.id]: http(),
  }
});

const bridgeAddress: Address = '0x6f978Fc5909CaCCA93fABe3BaC75C12a1856f8F7';
const sepoliaUSDCAddress: Address = '0xa3DD50f2481d655d9E6e1cB14F0BE417338BB6bb';
const shibuyaUSDCAddress: Address = '0xC6BfD304d993aBc9A00Af873465a05234cd79acD';

const Home: NextPage = () => {
  const [isMounted, setIsMounted] = useState(false);
  const { address, isConnected, connector, status } = useAccount();
  const [sepoliaBalance, setSepoliaBalance] = useState<number | null>(null);
  const [shibuyaBalance, setShibuyaBalance] = useState<number | null>(null);
  const [userSepoliaBalance, setUserSepoliaBalance] = useState<number | null>(null);
  const [userShibuyaBalance, setUserShibuyaBalance] = useState<number | null>(null);
  const [depositAmount, setDepositAmount] = useState<number>(0);

  const { data: sepoliaUSDCBalance } = useReadContract({
    address: sepoliaUSDCAddress,
    abi: erc20Abi,
    functionName: 'balanceOf',
    args: [bridgeAddress],
    chainId: sepolia.id
  });

  const { writeContract: writeDepositContract } = useWriteContract();
  const { writeContract: writeApproveContract } = useWriteContract();

  const handleDeposit = async () => {
    try {
      console.log("performing deposit")
      await writeDepositContract({
        abi: bridgeAbi,
        address: bridgeAddress,
        functionName: 'deposit',
        args: [BigInt(depositAmount)]},
        {
          onError: (error) => {
            console.error('Error during deposit:', error);
          },
          onSuccess: (data) => {
            console.log('Deposit successful:', data);
          },
          onSettled: (data, error) => {
            if (error) {
              console.error('Deposit settled with error:', error);
            } else {
              console.log('Deposit settled successfully:', data);
            }
          }
        }
      );
    } catch (error) {
      console.error('Unexpected error during deposit:', error);
    }
  };

  const { data: shibuyaUSDCBalance } = useReadContract({
    address: shibuyaUSDCAddress,
    abi: erc20Abi,
    functionName: 'balanceOf',
    args: [bridgeAddress],
    chainId: shibuya.id,
    config,
  });

  const { data: userSepoliaUSDCBalance } = useReadContract({
    address: sepoliaUSDCAddress,
    abi: erc20Abi,
    functionName: 'balanceOf',
    args: [address || "0x"],
    chainId: sepolia.id
  });

  const { data: userShibuyaUSDCBalance } = useReadContract({
    address: shibuyaUSDCAddress,
    abi: erc20Abi,
    functionName: 'balanceOf',
    args: [address || "0x"],
    chainId: shibuya.id,
    config,
  });

  useEffect(() => {
    setIsMounted(true);
  }, []);

  useEffect(() => {
    console.log(`address is ${address}, isConnected: ${isConnected}, connector: ${connector}, status: ${status}`);
  }, [address, isConnected, connector, status]);

  useEffect(() => {
    console.log('Fetching Sepolia USDC Balance with inputs:', {
      address: sepoliaUSDCAddress,
      abi: erc20Abi,
      functionName: 'balanceOf',
      args: [bridgeAddress],
      chainId: sepolia.id
    });
  }, []);

  useEffect(() => {
    console.log('Fetching Shibuya USDC Balance with inputs:', {
      address: shibuyaUSDCAddress,
      abi: erc20Abi,
      functionName: 'balanceOf',
      args: [bridgeAddress],
      chainId: shibuya.id,
      config,
    });
  }, []);

  useEffect(() => {
    if (!isConnected) {
      console.log('User is not connected');
    }
  }, [isConnected]);

  useEffect(() => {
    if (sepoliaUSDCBalance) {
      console.log('Sepolia USDC Balance:', sepoliaUSDCBalance);
      setSepoliaBalance(Number(sepoliaUSDCBalance));
    }
  }, [sepoliaUSDCBalance]);

  useEffect(() => {
    if (shibuyaUSDCBalance) {
      console.log('Shibuya USDC Balance:', shibuyaUSDCBalance);
      setShibuyaBalance(Number(shibuyaUSDCBalance));
    }
  }, [shibuyaUSDCBalance]);

  useEffect(() => {
    if (isConnected && address) {
      console.log('Fetching User Sepolia USDC Balance with inputs:', {
        address: sepoliaUSDCAddress,
        abi: erc20Abi,
        functionName: 'balanceOf',
        args: [address],
        chainId: sepolia.id
      });

      console.log('Fetching User Shibuya USDC Balance with inputs:', {
        address: shibuyaUSDCAddress,
        abi: erc20Abi,
        functionName: 'balanceOf',
        args: [address],
        chainId: shibuya.id,
        config,
      });
    }
  }, [isConnected, address]);

  useEffect(() => {
    if (userSepoliaUSDCBalance) {
      console.log('User Sepolia USDC Balance:', userSepoliaUSDCBalance);
      setUserSepoliaBalance(Number(userSepoliaUSDCBalance));
    } else {
      console.log('User Sepolia USDC Balance is null or undefined');
    }
  }, [userSepoliaUSDCBalance]);

  useEffect(() => {
    if (userShibuyaUSDCBalance) {
      console.log('User Shibuya USDC Balance:', userShibuyaUSDCBalance);
      setUserShibuyaBalance(Number(userShibuyaUSDCBalance));
    } else {
      console.log('User Shibuya USDC Balance is null or undefined');
    }
  }, [userShibuyaUSDCBalance]);

  return (
    <div className={styles.container}>
      <Head>
        <title>Analog AMM Bridge</title>
      </Head>

      <main className={styles.main}>
        <div className="flex justify-between items-center p-4">
          <ConnectButton />
        </div>
        {isMounted && isConnected && (
          <div className="flex justify-between items-center p-4">
            <p>Wallet is connected!</p>
          </div>
        )}
        <h1 className="text-center text-4xl font-bold my-8">Analog AMM Bridge</h1>
        <div className="text-center text-gray-500 text-sm underline cursor-pointer tooltip" data-tip="Analog Bridge is a smart contract-based bridge that facilitates trustless swap across arbitrary liquidity pairs across any chains. Unlike a ”lock and mint” bridge, introduces no new tokens. All native assets on each chain can be make an LP. Utilizes GMP (General Message Passing) to handle trustless cross-chain communication between 2 liquidity pools that live across distinct chain. The liquidity pools uses constant function market making ie. UniswapV2 algorithm">
          How does it work?
        </div>
        <div className="stats shadow mb-4">
          <div className="stat">
            <div className="stat-title">Bridge Sepolia Liquidity</div>
            <div className="stat-value white">
              ${sepoliaBalance !== null ? sepoliaBalance : 'Loading...'}
            </div>
            <div className="stat-desc">sepUSDC</div>
          </div>

          <div className="stat">
            <div className="stat-title">Bridge Shibuya Liquidity</div>
            <div className="stat-value white">
              ${shibuyaBalance !== null ? shibuyaBalance : 'Loading...'}
            </div>
            <div className="stat-desc">shUSDC</div>
          </div>
        </div>
        <div className="stats shadow mt-4">
          <div className="stat">
            <div className="stat-title">Your Sepolia Balance</div>
            <div className="stat-value white">
              ${userSepoliaBalance !== null ? userSepoliaBalance : '0'}
            </div>
            <div className="stat-desc">sepUSDC</div>
          </div>

          <div className="stat">
            <div className="stat-title">Your Shibuya Balance</div>
            <div className="stat-value white">
              ${userShibuyaBalance !== null ? userShibuyaBalance : '0'}
            </div>
            <div className="stat-desc">shUSDC</div>
          </div>
        </div>

        <div className="container mx-auto p-4">
          <div className={styles['card-wrapper']}> {/* Added wrapper */}
            <div className={styles['card-section']}>
              <h2 className="text-2xl font-bold mb-4 flex items-center">
                <CurrencyDollarIcon className="h-6 w-6 mr-2" />
                sepUSDC Faucet
              </h2>
              <div className={`${styles['info-section']} alert alert-info mb-4`}> {/* Updated */}
                <div>
                  <InformationCircleIcon className="h-6 w-6 mr-2" />
                  <span className="ml-2">
                    Mint sepUSDC on Sepolia network from the faucet and approve the USDC bridge contract prior to bridging (note: you must be the contract owner to mint)
                  </span>
                </div>
              </div>
              <div className="mb-4">
                <h3 className="text-lg font-semibold">
                  Mint $100 on Sepolia and approve the bridge
                </h3>
              </div>
              <div className="flex space-x-4">
                <button className="bg-gray-400 text-white font-bold py-2 px-4 rounded" disabled>
                  1. Mint
                </button>
                <button 
                  className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
                  onClick={() => 
                    writeApproveContract({ 
                      abi: erc20Abi,
                      address: sepoliaUSDCAddress,
                      functionName: 'approve',
                      args: [
                        bridgeAddress,
                        BigInt(100),
                      ],
                   })
                  }
                >
                  2. Approve
                </button>
              </div>
            </div>
          </div>

          <div className={styles['card-wrapper']}> {/* Added wrapper */}
            <div className={styles['card-section']}>
              <h2 className="text-2xl font-bold mb-4 flex items-center">
                <LightningBoltIcon className="h-6 w-6 mr-2" />
                Bridge
              </h2>
              <div className={`${styles['info-section']} alert alert-info mb-4`}> {/* Updated */}
                <div>
                  <InformationCircleIcon className="h-6 w-6 mr-2" />
                  <span className="ml-2">
                    Bridge sepUSDC from Sepolia to shiUSDC living in Shibuya via Analog GMP rail. Transaction will take a while to confirm, but token will automatically be released at the destination chain
                  </span>
                </div>
              </div>
              <div className="mb-4">
              <input
                type="number"
                placeholder="Amount"
                className="input input-bordered w-full max-w-xs mr-2"
                value={depositAmount}
                onChange={(e) => setDepositAmount(Number(e.target.value))} // Update state on input change
              />
                <span className="text-lg font-semibold">
                  sepUSDC to shUSDC
                </span>
              </div>
              <div>
                <button 
                  className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
                  onClick={handleDeposit}
                >
                  Bridge
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>

      <footer className={styles.footer}>
        <a href="https://rainbow.me" rel="noopener noreferrer" target="_blank">
          Made for Analog HackerEarth Hack
        </a>
      </footer>
    </div>
  );
};

export default Home;