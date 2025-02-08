import { ExclamationCircleIcon } from '@heroicons/react/24/outline';
import {Button} from '@heroui/react';

const NotFound = () => {
    return (		
        <div className="absolute flex flex-col sm:text-3xl font-mono w-full h-full justify-between border border-green-300 rounded-md shadow-sm shadow-green-200">
            <div className="flex w-full h-5 justify-between text-sm text-[#baffdb] border-green-300 border-b pl-1 pr-0.5">
                <span className="font-semibold">aipfs-library: Sorry, you got lost in an unknown dimension. </span>
            </div>
			<div className="flex flex-col items-center justify-center w-full h-full">
				<ExclamationCircleIcon className="w-24 h-24 text-red-500" />
            	<div className="mt-4 text-4xl font-bold text-gray-800 leading-relaxed">404 - Page Not Found</div>
            	<div className="mt-4 text-lg text-gray-600 leading-relaxed">Sorry, the page you are looking for does not exist.</div>
				<Button href={`${window.location.origin}/#/`} className="mt-4">Go to Home</Button>
			</div>
    	</div>
    );
};

export default NotFound;
