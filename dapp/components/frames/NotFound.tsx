import { ExclamationCircleIcon } from '@heroicons/react/24/outline';
import {Button} from '@heroui/react';
import TerminalFrame from '../elements/TerminalFrame';

const NotFound = () => {
    return (	
		<TerminalFrame subTitle="Sorry, you got lost in an unknown dimension.">
			<div className="flex flex-col items-center justify-center w-full h-full">
				<ExclamationCircleIcon className="w-24 h-24 text-red-500" />
            	<div className="mt-4 text-4xl font-bold text-gray-800 leading-relaxed">404 - Page Not Found</div>
            	<div className="mt-4 text-lg text-gray-600 leading-relaxed">Sorry, the page you are looking for does not exist.</div>
				<Button href={`${window.location.origin}/#/`} className="mt-4">Go to Home</Button>
			</div>
		</TerminalFrame>	
    );
};

export default NotFound;
