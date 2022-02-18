import React from "react"
import { LoginPage } from "../../components"
import { connect } from "react-redux"
import {EuiGlobalToastList, EuiLoadingSpinner} from "@elastic/eui";

function ProtectedRoute({
    user,
    userLoaded,
    isAuthenticated,
    component: Compnent,
    redirectTitle = "Access Denied",
    redirectMessage = `Authenticated users only. Login here or create new account to view that page.`,
    ...props
}) {
    const [toasts, setToasts] = React.useState([
        {
            id: "auth-redirect-toast",
            title: redirectTitle,
            color: "warning",
            iconType: "alert",
            toastLifeTimeMs: 15000,
            text: <p>{redirectMessage}</p>
        }
    ])
    if (!userLoaded) return <EuiLoadingSpinner size="xl" />
    const isAuthed = isAuthenticated && Boolean(user?.email)
    if (!isAuthed) {
        return (
            <>
                <LoginPage />
                <EuiGlobalToastList
                    toasts={toasts}
                    dismissToast={() => setToasts([])}
                    toastLifeTimeMs={15000}
                    side="right"
                    className="auth-toast-list"
                />
            </>
        )
    }
    return <Compnent { ...props} />
}

export default connect((state) => ({
    user: state.auth.user,
    isAuthenticated: state.auth.isAuthenticated,
    userLoaded: state.auth.userLoaded
}))(ProtectedRoute)