
import { FaRegWindowRestore ,FaXmark,FaRegWindowMinimize} from "react-icons/fa6"

export default function Terminal() {
	return (
		<div className="flex flex-col sm:text-3xl font-mono w-full h-full justify-between border border-green-300 rounded-md shadow-sm shadow-green-200">
          <div className="flex w-full h-5 justify-between text-sm text-[#baffdb] border-green-300 border-b pl-1 pr-0.5">
            <span className="font-semibold">Terminal</span>
            <div className="flex flex-row gap-1 items-center justify-center">
              <FaRegWindowMinimize />
              <FaRegWindowRestore className="ml-1" />
              <FaXmark className="text-lg" />
            </div>
          </div>
          <span className="flex w-full h-full items-start justify-start halo-text pl-3 py-2 text-sm">
            {'Agent: How can I help you today?'}
          </span>
          <div className="flex w-full items-start halo-text pl-3 pb-2 text-xl sm:text-2xl">
            <span>{'>_'}</span>
          </div>
        </div>
	)
}