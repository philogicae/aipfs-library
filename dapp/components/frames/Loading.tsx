'use client'

import PageWrapper from "@components/layout/PageWrapper"
import TerminalFrame from "@components/elements/TerminalFrame"

export default function Loading() {
	return (
		<PageWrapper>
			<TerminalFrame subTitle="loading...">
				<div className="h-12 w-12 animate-spin rounded-full border-3 border-solid border-current border-r-transparent motion-reduce:animate-[spin_1.5s_linear_infinite]"/>
				<div className="h-5"/>
			</TerminalFrame>
		</PageWrapper>
	)
}
