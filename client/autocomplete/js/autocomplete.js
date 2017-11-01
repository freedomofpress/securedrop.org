import React, { PureComponent } from 'react'
import { render } from 'react-dom'
import axios from 'axios'

import Autocomplete from './components/Autocomplete'


axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'


window.renderAutocompleteWidget = (id, name, value, type, canCreate, isSingle, apiBase) => {
	if (apiBase === '') {
		apiBase = "/admin/autocomplete/"
	}
	render(
		<Autocomplete
			name={name}
			value={value}
			type={type}
			canCreate={canCreate}
			isSingle={isSingle}
			apiBase={apiBase}
		/>,
		document.getElementById(id)
	)
}
