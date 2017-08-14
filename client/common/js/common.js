import classlist from 'classlist-polyfill'
import 'element-dataset'
import 'normalize-css/normalize.css'
import axios from 'axios'

axios.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest'
axios.defaults.xsrfCookieName = 'csrftoken'
axios.defaults.xsrfHeaderName = 'X-CSRFToken'

import '../sass/common.sass'
