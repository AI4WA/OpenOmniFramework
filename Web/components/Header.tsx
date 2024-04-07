'use client'
import Link from 'next/link';
import React from 'react';
import IconButton from '@mui/material/IconButton';
import Menu from '@mui/material/Menu';
import MenuItem from '@mui/material/MenuItem';
import AccountCircle from '@mui/icons-material/AccountCircle';
import {store} from "@/store";
import {logout} from "@/store/authSlices";
import {useRouter} from 'next/navigation';

const Header = () => {
    const [anchorEl, setAnchorEl] = React.useState<HTMLElement | null>(null);
    const open = Boolean(anchorEl);
    const router = useRouter();

    // Correctly handle the menu event without casting
    const handleMenu = (event: React.MouseEvent<HTMLButtonElement>) => {
        setAnchorEl(event.currentTarget);
    };


    const handleClose = () => {
        setAnchorEl(null);
    };

    const goToProfile = () => {
        handleClose();
        router.push('/profile');
    }

    const clickLogout = async () => {
        handleClose();
        store.dispatch(logout());
        localStorage.removeItem("access");
        localStorage.removeItem("refresh");
        router.push('/');
    }

    return (
        <header className="bg-white shadow-md">
            <div className="container mx-auto px-4 py-4 flex justify-between items-center">
                <nav>
                    <Link href="/dashboard">
                        <p className="text-blue-600 hover:text-blue-800 font-semibold">Dashboard</p>
                    </Link>
                </nav>
                <div>
                    <IconButton
                        size="large"
                        aria-label="account of current user"
                        aria-controls="menu-appbar"
                        aria-haspopup="true"
                        onClick={handleMenu}
                        color="inherit"
                    >
                        <AccountCircle/>
                    </IconButton>
                    <Menu
                        id="menu-appbar"
                        anchorEl={anchorEl}
                        anchorOrigin={{
                            vertical: 'top',
                            horizontal: 'right',
                        }}
                        keepMounted
                        transformOrigin={{
                            vertical: 'top',
                            horizontal: 'right',
                        }}
                        open={open}
                        onClose={handleClose}
                    >
                        <MenuItem onClick={goToProfile}>Profile</MenuItem>
                        <MenuItem onClick={clickLogout}>Logout</MenuItem>
                    </Menu>
                </div>
            </div>
        </header>
    );
};

export default Header;
