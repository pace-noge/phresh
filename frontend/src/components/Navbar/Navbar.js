import React from "react"
import { Actions as authActions } from "../../redux/auth"
import {
    EuiIcon,
    EuiHeader,
    EuiHeaderSection,
    EuiHeaderSectionItem,
    EuiHeaderLink,
    EuiHeaderLinks,
    EuiHeaderSectionItemButton,
    EuiAvatar, EuiFlexItem, EuiFlexGroup, EuiLink, EuiPopover
} from "@elastic/eui"
import { Link } from "react-router-dom"
import loginIcon from "../../assets/img/loginIcon.svg"
import styled from "styled-components"
import { connect } from "react-redux"

const LogoSection = styled(EuiHeaderLink)`
    padding: 0 2rem;
`
const AvatarMenu = styled.div`
    display: flex;
    justify-content: space-between;
    min-width: 300px;
    
    & .avatar-actions {
        margin-left: 2rem;
    }
`

function Navbar({ user, logUserOut, ...props }) {
    const [avatarMenuOpen, setAvatarMenuOpen] = React.useState(false)
    const toggleAvatarMenu = () => setAvatarMenuOpen(!avatarMenuOpen)
    const closeAvatarMenu = () => setAvatarMenuOpen(false)

    const handleLogout = () => {
        closeAvatarMenu()
        logUserOut()
    }

    const avatarButton = (
        <EuiHeaderSectionItemButton
            aria-label="User Avatar"
            onClick={() => user?.profile && toggleAvatarMenu()}
        >
            {user?.profile ? (
                <EuiAvatar
                    size="l"
                    name={user.profile.full_name || "Anonympus"}
                    initialsLength={2}
                    imageUrl={user.profile.image}
                />
            ) : (
                <Link to="/login">
                    <EuiAvatar size="l" color="#1E90FF" name="user" imageUrl={loginIcon} />
                </Link>
            )}
        </EuiHeaderSectionItemButton>
    )

    const renderAvatarMenu = () => {
        if (!user?.profile) return null

        return (
            <AvatarMenu>
                <EuiAvatar
                    size="xl"
                    name={user.profile.full_name || "Anonymous"}
                    initialsLength={2}
                    imageUrl={user.profile.image}
                />
                <EuiFlexGroup direction="column" className="avatar-actions">
                    <EuiFlexItem grow={1}>
                        <p>
                            {user.email} - {user.username}
                        </p>
                    </EuiFlexItem>

                    <EuiFlexItem grow={1}>
                        <EuiFlexGroup justifyContent="spaceBetween">
                            <EuiFlexItem grow={1}>
                                <Link to="/profile">Profile</Link>
                            </EuiFlexItem>
                            <EuiFlexItem grow={1}>
                                <EuiLink onClick={() => handleLogout()}>Log out</EuiLink>
                            </EuiFlexItem>
                        </EuiFlexGroup>
                    </EuiFlexItem>
                </EuiFlexGroup>
            </AvatarMenu>
        )
    }

    return (
        <EuiHeader style={props.style || {}}>
            <EuiHeaderSection>
                <EuiHeaderSectionItem border="right">
                    <LogoSection href="/">
                        <EuiIcon type="cloudDrizzle" color="#1E90FF" size="l" /> Phresh
                    </LogoSection>
                </EuiHeaderSectionItem>
                <EuiHeaderSectionItem border="right">
                    <EuiHeaderLinks aria-label="app navigation links">
                        <EuiHeaderLink iconType="tear" href="#">
                            Find Cleaner
                        </EuiHeaderLink>

                        <EuiHeaderLink iconType="tag" href="#">
                            Find Jobs
                        </EuiHeaderLink>

                        <EuiHeaderLink iconType="help" href="#">
                            Help
                        </EuiHeaderLink>

                    </EuiHeaderLinks>
                </EuiHeaderSectionItem>
            </EuiHeaderSection>

            <EuiHeaderSection>
                <EuiPopover
                    id="avatar-menu"
                    isOPen={avatarMenuOpen}
                    closePopOver={closeAvatarMenu}
                    anchorPosition="downRight"
                    button={avatarButton}
                    panelPaddingSize="l"
                    >
                    {renderAvatarMenu()}
                </EuiPopover>
            </EuiHeaderSection>

        </EuiHeader>
    )
}

export default connect((state) => ({ user: state.auth.user }), {
    logUserOut: authActions
})(Navbar)