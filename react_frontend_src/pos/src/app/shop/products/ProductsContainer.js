import { connect } from 'react-redux'
import { injectIntl } from 'react-intl';
import { withRouter } from 'react-router'

import { appOperations } from '../../duck'
import Products from './Products';


const mapStateToProps = state => 
    ({
        app: state.app,
        loaded: state.shop.products.loaded,
        products: state.shop.products.data
    })

const mapDispatchToProps = dispatch =>
    ({
        setPageTitle(title) {
            dispatch(appOperations.setPageTitle(title))
        }
    })

const ProductsContainer = withRouter(injectIntl(connect(
    mapStateToProps,
    mapDispatchToProps
)(Products)))

export default ProductsContainer