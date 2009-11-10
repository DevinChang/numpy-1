/*
 * Low-level routines related to IEEE-754 format
 */
#include "npy_math_common.h"
#include "npy_math_private.h"

#ifndef HAVE_COPYSIGN
double npy_copysign(double x, double y)
{
    npy_uint32 hx, hy;
    GET_HIGH_WORD(hx, x);
    GET_HIGH_WORD(hy, y);
    SET_HIGH_WORD(x, (hx & 0x7fffffff) | (hy & 0x80000000));
    return x;
}
#endif

#if !defined(HAVE_DECL_SIGNBIT)
#include "_signbit.c"

int _npy_signbit_f(float x)
{
    return _npy_signbit_d((double) x);
}

int _npy_signbit_ld(long double x)
{
    return _npy_signbit_d((double) x);
}
#endif

/*
 * nextafter code taken from BSD math lib, the code contains the following
 * notice:
 *
 * ====================================================
 * Copyright (C) 1993 by Sun Microsystems, Inc. All rights reserved.
 *
 * Developed at SunPro, a Sun Microsystems, Inc. business.
 * Permission to use, copy, modify, and distribute this
 * software is freely granted, provided that this notice
 * is preserved.
 * ====================================================
 */
#ifndef HAVE_NEXTAFTER
double npy_nextafter(double x, double y)
{
    volatile double t;
    npy_int32 hx, hy, ix, iy;
    npy_uint32 lx, ly;

    EXTRACT_WORDS(hx, lx, x);
    EXTRACT_WORDS(hy, ly, y);
    ix = hx & 0x7fffffff;       /* |x| */
    iy = hy & 0x7fffffff;       /* |y| */

    if (((ix >= 0x7ff00000) && ((ix - 0x7ff00000) | lx) != 0) ||        /* x is nan */
        ((iy >= 0x7ff00000) && ((iy - 0x7ff00000) | ly) != 0))  /* y is nan */
        return x + y;
    if (x == y)
        return y;               /* x=y, return y */
    if ((ix | lx) == 0) {       /* x == 0 */
        INSERT_WORDS(x, hy & 0x80000000, 1);    /* return +-minsubnormal */
        t = x * x;
        if (t == x)
            return t;
        else
            return x;           /* raise underflow flag */
    }
    if (hx >= 0) {              /* x > 0 */
        if (hx > hy || ((hx == hy) && (lx > ly))) {     /* x > y, x -= ulp */
            if (lx == 0)
                hx -= 1;
            lx -= 1;
        } else {                /* x < y, x += ulp */
            lx += 1;
            if (lx == 0)
                hx += 1;
        }
    } else {                    /* x < 0 */
        if (hy >= 0 || hx > hy || ((hx == hy) && (lx > ly))) {  /* x < y, x -= ulp */
            if (lx == 0)
                hx -= 1;
            lx -= 1;
        } else {                /* x > y, x += ulp */
            lx += 1;
            if (lx == 0)
                hx += 1;
        }
    }
    hy = hx & 0x7ff00000;
    if (hy >= 0x7ff00000)
        return x + x;           /* overflow  */
    if (hy < 0x00100000) {      /* underflow */
        t = x * x;
        if (t != x) {           /* raise underflow flag */
            INSERT_WORDS(y, hx, lx);
            return y;
        }
    }
    INSERT_WORDS(x, hx, lx);
    return x;
}
#endif

#ifndef HAVE_NEXTAFTERF
float npy_nextafterf(float x, float y)
{
    volatile float t;
    npy_int32 hx, hy, ix, iy;

    GET_FLOAT_WORD(hx, x);
    GET_FLOAT_WORD(hy, y);
    ix = hx & 0x7fffffff;       /* |x| */
    iy = hy & 0x7fffffff;       /* |y| */

    if ((ix > 0x7f800000) ||    /* x is nan */
        (iy > 0x7f800000))      /* y is nan */
        return x + y;
    if (x == y)
        return y;               /* x=y, return y */
    if (ix == 0) {              /* x == 0 */
        SET_FLOAT_WORD(x, (hy & 0x80000000) | 1); /* return +-minsubnormal */
        t = x * x;
        if (t == x)
            return t;
        else
            return x;           /* raise underflow flag */
    }
    if (hx >= 0) {              /* x > 0 */
        if (hx > hy) {          /* x > y, x -= ulp */
            hx -= 1;
        } else {                /* x < y, x += ulp */
            hx += 1;
        }
    } else {                    /* x < 0 */
        if (hy >= 0 || hx > hy) {       /* x < y, x -= ulp */
            hx -= 1;
        } else {                /* x > y, x += ulp */
            hx += 1;
        }
    }
    hy = hx & 0x7f800000;
    if (hy >= 0x7f800000)
        return x + x;           /* overflow  */
    if (hy < 0x00800000) {      /* underflow */
        t = x * x;
        if (t != x) {           /* raise underflow flag */
            SET_FLOAT_WORD(y, hx);
            return y;
        }
    }
    SET_FLOAT_WORD(x, hx);
    return x;
}
#endif

#ifndef HAVE_NEXTAFTERL
npy_longdouble npy_nextafterl(npy_longdouble x, npy_longdouble y)
{
    volatile npy_longdouble t;
    union IEEEl2bits ux, uy;

    ux.e = x;
    uy.e = y;

    if ((ux.bits.exp == 0x7fff &&
         ((ux.bits.manh & ~LDBL_NBIT) | ux.bits.manl) != 0) ||
        (uy.bits.exp == 0x7fff &&
         ((uy.bits.manh & ~LDBL_NBIT) | uy.bits.manl) != 0)) {
        return x + y;           /* x or y is nan */
    }
    if (x == y) {
        return y;               /* x=y, return y */
    }
    if (x == 0.0) {
        ux.bits.manh = 0;       /* return +-minsubnormal */
        ux.bits.manl = 1;
        ux.bits.sign = uy.bits.sign;
        t = ux.e * ux.e;
        if (t == ux.e) {
            return t;
        } else {
            return ux.e;        /* raise underflow flag */
        }
    }
    if (x > 0.0 ^ x < y) {      /* x -= ulp */
        if (ux.bits.manl == 0) {
            if ((ux.bits.manh & ~LDBL_NBIT) == 0) {
                ux.bits.exp -= 1;
            }
            ux.bits.manh = (ux.bits.manh - 1) | (ux.bits.manh & LDBL_NBIT);
        }
        ux.bits.manl -= 1;
    } else {                    /* x += ulp */
        ux.bits.manl += 1;
        if (ux.bits.manl == 0) {
            ux.bits.manh = (ux.bits.manh + 1) | (ux.bits.manh & LDBL_NBIT);
            if ((ux.bits.manh & ~LDBL_NBIT) == 0) {
                ux.bits.exp += 1;
            }
        }
    }
    if (ux.bits.exp == 0x7fff) {
        return x + x;           /* overflow  */
    }
    if (ux.bits.exp == 0) {     /* underflow */
        mask_nbit_l(ux);
        t = ux.e * ux.e;
        if (t != ux.e) {        /* raise underflow flag */
            return ux.e;
        }
    }
    return ux.e;
}
#endif

/*
 * Decorate all the math functions which are available on the current platform
 */

#ifdef HAVE_NEXTAFTERF
float npy_nextafterf(float x, float y)
{
    return nextafterf(x, y);
}
#endif

#ifdef HAVE_NEXTAFTER
double npy_nextafter(double x, double y)
{
    return nextafter(x, y);
}
#endif

#ifdef HAVE_NEXTAFTERL
npy_longdouble npy_nextafterl(npy_longdouble x, npy_longdouble y)
{
    return nextafterl(x, y);
}
#endif
