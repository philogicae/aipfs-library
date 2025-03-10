'use client'

import Home from '@components/frames/Home'
import Loading from '@components/frames/Loading'
import { NotFoundIn } from '@components/frames/NotFound'
import Unavailable from '@components/frames/Unavailable'
import { useEffect, useState } from 'react'
import { createHashRouter } from 'react-router'
import { RouterProvider } from 'react-router/dom'

const hydrateFallbackElement = <Loading />

export default function Router() {
	const [hashRouter, setHashRouter] = useState<any>()

	if (typeof window !== 'undefined') {
		const storedVersion = localStorage.getItem('appVersion')
		if (storedVersion !== process.env.version) {
			localStorage.setItem('appVersion', process.env.version as string)
			window.location.reload()
		}
	}

	useEffect(() => {
		console.log(`appVersion v${process.env.version}`)
		setHashRouter(
			createHashRouter([
				{
					path: '',
					element: <Home />,
					hydrateFallbackElement,
				},
				{
					path: 'down',
					element: <Unavailable />,
					hydrateFallbackElement,
				},
				{
					path: '*',
					element: <NotFoundIn />,
					hydrateFallbackElement,
				},
			])
		)
	}, [])

	if (!hashRouter) return <Loading />
	return <RouterProvider router={hashRouter} />
}
