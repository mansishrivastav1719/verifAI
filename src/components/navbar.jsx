const Navbar = ({ onNavClick }) => {
    const handleClick = (section) => {
        onNavClick(section);
    };

    return (
        <nav style={styles.nav}>
            <div style={styles.logoContainer}>
                <img src="/vite.svg" alt="logo" style={styles.logoImage} />
                <h2 style={styles.logo} className="text-3xl">verifAi</h2>
            </div>
            <ul style={styles.menu}>
                <li onClick={() => handleClick('detect')} style={styles.menuItem}>Detect</li>
                <li onClick={() => handleClick('howitworks')} style={styles.menuItem}>How It Works</li>
                <li onClick={() => handleClick('requirements')} style={styles.menuItem}>Requirements</li>
                <li onClick={() => handleClick('footer')} style={styles.menuItem}>Team</li>
            </ul>
        </nav>
    );
};

const styles = {
    nav: {
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: "16px 60px",
        backgroundColor: "#fff",
    },
    logoContainer: {
        display: "flex",
        alignItems: "center",
        gap: "10px",
    },
    logoImage: {
        width: "40px",
        height: "40px",
    },
    logo: {
        color: "#3b82f6",
    },
    menu: {
        display: "flex",
        listStyle: "none",
        gap: "24px",
        cursor: "pointer",
    },
    menuItem: {
        cursor: "pointer",
        transition: "color 0.3s ease",
    }
};

export default Navbar;
