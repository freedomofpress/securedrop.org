import React, { PureComponent } from 'react'

import Suggestions from './Suggestions'


class Multi extends PureComponent {
	constructor(...args) {
		super(...args)

		this.handleClick = this.handleClick.bind(this)
	}

	handleClick(suggestion) {
		const { onClick, selections } = this.props
		onClick(selections.concat(suggestion))
	}

	handleRemove(page) {
		const { onClick, selections } = this.props
		onClick(selections.filter(({ id }) => id !== page.id))
	}

	render() {
		const {
			selections,
			onChange,
			onCreate,
			canCreate,
			input,
		} = this.props

		const suggestions = this.props.suggestions.filter(suggestion => {
			if (!selections) {
				return true
			}
			return selections.every(({ id }) => id !== suggestion.id)
		})

		return (
			<span className="autocomplete-layout">
				<span className="autocomplete-layout__item">
					<Suggestions
						suggestions={suggestions}
						onClick={this.handleClick}
						onChange={onChange}
						onCreate={onCreate}
						canCreate={canCreate}
						input={input}
						inputElm={this.inputElm}
					/>
				</span>

				<span className="autocomplete-layout__item autocomplete-layout__item--padded">
					{selections.length === 0 && (
						<span>Nothing selected.</span>
					)}
					{selections.map(selection =>
						<div
							key={selection.id}
							className="selection"
						>
							<span className="selection__label">{selection.label}</span>

							<button
								type="button"
								className="selection__button"
								onClick={this.handleRemove.bind(this, selection)}
							>
								<svg className="selection__icon" viewBox="0 0 1792 1792" xmlns="http://www.w3.org/2000/svg"><path d="M1490 1322q0 40-28 68l-136 136q-28 28-68 28t-68-28l-294-294-294 294q-28 28-68 28t-68-28l-136-136q-28-28-28-68t28-68l294-294-294-294q-28-28-28-68t28-68l136-136q28-28 68-28t68 28l294 294 294-294q28-28 68-28t68 28l136 136q28 28 28 68t-28 68l-294 294 294 294q28 28 28 68z"/></svg>
								<span className="sr-only">Remove</span>
							</button>
						</div>
					)}
				</span>
			</span>
		)
	}
}


Multi.defaultProps = {
	selections: [],
}


export default Multi
