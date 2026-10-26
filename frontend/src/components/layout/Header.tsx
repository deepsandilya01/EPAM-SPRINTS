import React, { useState } from 'react'
import {
  Calendar,
  ChevronDown,
  Play,
  CheckCircle2,
  ChevronRight,
  ShieldAlert,
  BarChart3,
  Network,
} from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'
import { useAppDispatch, useAppSelector } from '@/store/hooks'
import { setIsSimulating } from '@/store/slices/graphUiSlice'

export const Header: React.FC = () => {
  const dispatch = useAppDispatch()
  const location = useLocation()
  const { traceDirection, isSimulating, selectedSupplier } = useAppSelector(
    (state) => state.graphUi
  )
  const [simulationToast, setSimulationToast] = useState<string | null>(null)

  const handleRunSimulation = () => {
    dispatch(setIsSimulating(true))
    setSimulationToast('Simulating supply-chain disruption propagation...')
    setTimeout(() => {
      dispatch(setIsSimulating(false))
      setSimulationToast(
        `Local demo simulation complete: 10 downstream entities reached from ${selectedSupplier} with estimated buffer absorption of 3.2 days.`
      )
      setTimeout(() => {
        setSimulationToast(null)
      }, 5000)
    }, 800)
  }

  const directionLabel =
    traceDirection === 'downstream' ? 'Downstream Trace' : 'Upstream Trace'

  return (
    <>
      <header className="h-14 bg-white border-b border-slate-200 px-6 flex items-center justify-between sticky top-0 z-20 shadow-xs">
        <div className="flex items-center gap-2 text-xs">
          <Link
            to="/graph-explorer"
            className="text-slate-500 hover:text-slate-800 transition-colors"
          >
            Supply Chain
          </Link>
          <ChevronRight className="w-3 h-3 text-slate-400" />
          <Link
            to="/graph-explorer"
            className="text-slate-500 hover:text-slate-800 transition-colors"
          >
            Graph Explorer
          </Link>
          <ChevronRight className="w-3 h-3 text-slate-400" />
          <span className="font-bold text-slate-900">{directionLabel}</span>

          <div className="ml-6 pl-6 border-l border-slate-200 flex items-center gap-3">
            <Link
              to="/graph-explorer"
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-medium transition-colors ${
                location.pathname === '/graph-explorer' || location.pathname === '/'
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <Network className="w-3.5 h-3.5" />
              <span>Explorer</span>
            </Link>

            <Link
              to="/validation"
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-medium transition-colors ${
                location.pathname === '/validation'
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <ShieldAlert className="w-3.5 h-3.5" />
              <span>Validation</span>
            </Link>

            <Link
              to="/performance"
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-medium transition-colors ${
                location.pathname === '/performance'
                  ? 'bg-blue-50 text-blue-700'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <BarChart3 className="w-3.5 h-3.5" />
              <span>Benchmarks</span>
            </Link>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="button"
            className="flex items-center gap-2 px-3 py-1.5 bg-white border border-slate-200 rounded-md shadow-xs text-xs font-medium text-slate-700 hover:border-slate-300 transition-colors"
          >
            <Calendar className="w-3.5 h-3.5 text-slate-500" />
            <span>Feb 5, 2025</span>
            <ChevronDown className="w-3 h-3 text-slate-400" />
          </button>

          <button
            type="button"
            onClick={handleRunSimulation}
            disabled={isSimulating}
            className="flex items-center gap-1.5 px-3.5 py-1.5 bg-[#0f172a] hover:bg-slate-800 active:bg-slate-950 text-white text-xs font-semibold rounded-md shadow-xs transition-colors cursor-pointer disabled:opacity-75"
          >
            {isSimulating ? (
              <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
            ) : (
              <Play className="w-3.5 h-3.5 fill-white" />
            )}
            <span>{isSimulating ? 'Simulating...' : 'Run Simulation'}</span>
          </button>

          <div
            className="w-8 h-8 rounded-full bg-blue-600 text-white font-bold text-xs flex items-center justify-center shadow-xs cursor-pointer select-none"
            title="User: Deep Sandilya"
          >
            D
          </div>
        </div>
      </header>

      {simulationToast && (
        <div className="bg-blue-600 text-white text-xs py-2 px-6 flex items-center justify-between shadow-md transition-all animate-in fade-in slide-in-from-top-1">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 shrink-0 text-blue-200" />
            <span>{simulationToast}</span>
          </div>
          <button
            onClick={() => setSimulationToast(null)}
            className="text-blue-200 hover:text-white text-xs underline ml-4"
          >
            Dismiss
          </button>
        </div>
      )}
    </>
  )
}
